import base64
import os
import re

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from werkzeug.utils import secure_filename

from src import calculos

load_dotenv()

app = Flask(__name__)

# Configuración de subida de archivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB máximo
EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "pdf"}


def extension_permitida(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS


SYSTEM_PROMPT_NARRADOR = """Eres "VólticvS", un asesor energético con buen humor de Chile.
Ya se calcularon con exactitud el consumo y el ahorro potencial del hogar del usuario;
tu única tarea es redactar un resumen breve (4 a 6 frases) explicando los resultados de
forma cálida, clara y con un toque de humor.

REGLA ABSOLUTA: no inventes ni cambies ningún número. Usa EXACTAMENTE los valores en
kWh y CLP que te entrego. Si necesitas redondear, usa el mismo valor que te dieron.
Destaca cuál es la mayor oportunidad de ahorro y da 5 - 7 recomendaciones concretas.
No repitas toda la lista de artefactos, enfócate en lo más relevante.

Debes realizar una proyeccion en el tiempo ademas a los 3 meses, 6 meses, 12 meses, a los 2 años y 5 años.
"""


def generar_narrativa(resumen: dict) -> str:
    try:
        llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0.5,
            api_key=os.getenv("GROQ_API_KEY"),
        )
        mensaje = f"Estos son los resultados calculados para este hogar: {resumen}"
        respuesta = llm.invoke([SystemMessage(content=SYSTEM_PROMPT_NARRADOR), HumanMessage(content=mensaje)])
        return respuesta.content
    except Exception:
        # Si no hay API key configurada o falla la llamada, igual entregamos
        # un resumen útil basado 100% en los números ya calculados.
        return (
            f"Tu consumo estimado es de {resumen['total_kwh_mes']} kWh al mes "
            f"(~${resumen['total_clp_mes']:,.0f} CLP). Podrías ahorrar hasta "
            f"${resumen['ahorro_potencial_clp_mes']:,.0f} CLP al mes aplicando los cambios sugeridos."
        )


def generar_recomendaciones(desglose: list) -> list:
    """
    Convierte el desglose numérico en frases de recomendación concretas,
    cada una con el ahorro mensual y anual ya calculado (determinista, sin IA).
    Ordenadas de mayor a menor impacto de ahorro.
    """
    candidatas = []
    for item in desglose:
        ahorro_mes = item.get("ahorro_clp_mes", 0)
        if not ahorro_mes or ahorro_mes <= 0:
            continue
        ahorro_anio = round(ahorro_mes * 12)
        nombre = item["nombre"]

        if "kwh_mes_si_fuera_led" in item:
            frase = f"Cambia tu {nombre.lower()} a LED"
        elif "kwh_mes_llenado_habitual" in item:
            frase = "Hierve solo el agua que necesitas en vez de llenar el hervidor completo"
        elif "kwh_mes_optimo" in item:
            frase = f"Desconecta {nombre.lower()} cuando no lo estés usando"
        else:
            frase = f"Optimiza el uso de {nombre.lower()}"

        texto = f"{frase}: ahorras ${ahorro_mes:,.0f}/mes (${ahorro_anio:,.0f} al año)."
        candidatas.append((ahorro_mes, texto))

    candidatas.sort(key=lambda par: par[0], reverse=True)
    return [texto for _, texto in candidatas]


@app.route("/api/paises")
def paises():
    datos = {k: v for k, v in calculos.REFERENCIA["paises"].items() if not k.startswith("_")}
    return jsonify(datos)


@app.route("/api/interpretar-campo", methods=["POST"])
def interpretar_campo():
    """
    Llamada Opcional #1 (solo cuando el usuario escribe "Otro" en tipo de inmueble).
    Recibe { campo: "tipo_inmueble", texto: "..." } y mapea el texto libre a uno
    de los valores conocidos del sistema usando el LLM.
    Máximo 1 llamada LLM por campo libre ingresado.
    """
    data = request.get_json(force=True) or {}
    campo = data.get("campo", "")
    texto = (data.get("texto") or "").strip()

    if not texto:
        return jsonify({"valor_mapeado": "Casa", "fuente": "fallback_vacio"})

    VALORES_INMUEBLE = ["Casa", "Casa pareada", "Departamento", "Casa móvil", "Otro"]
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        # Sin API key: devolvemos el texto tal cual como fallback limpio
        return jsonify({"valor_mapeado": texto[:50], "fuente": "fallback_sin_api"})

    try:
        llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0,
            api_key=groq_api_key,
        )
        prompt = (
            f"El usuario describió su tipo de vivienda como: '{texto}'.\n"
            f"Mapea esto al valor MÁS CERCANO de esta lista exacta: {VALORES_INMUEBLE}.\n"
            f"Responde SOLO con el valor exacto de la lista, sin explicaciones ni puntos."
        )
        respuesta = llm.invoke([HumanMessage(content=prompt)])
        valor = respuesta.content.strip().strip("\"'.")
        # Validar que el valor esté en la lista permitida
        if valor not in VALORES_INMUEBLE:
            valor = "Casa"
        return jsonify({"valor_mapeado": valor, "fuente": "llm"})
    except Exception as e:
        return jsonify({"valor_mapeado": "Casa", "fuente": "fallback_error", "detalle": str(e)})


@app.route("/api/comparar", methods=["POST"])
def comparar():
    datos = request.get_json(force=True)
    try:
        resultado = calculos.comparar_categoria(
            datos["categoria"], float(datos["horas_uso_diario"]), float(datos.get("tarifa_clp_kwh", 230))
        )
        return jsonify(resultado)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/calcular", methods=["POST"])
def calcular():
    datos = request.get_json(force=True)
    tarifa = float(datos.get("tarifa_clp_kwh", 150))

    desglose = []
    total_kwh_mes = 0.0
    ahorro_potencial_clp_mes = 0.0

    # Electrodomésticos de la tabla de referencia
    for item in datos.get("electrodomesticos", []):
        try:
            resultado = calculos.consumo_mensual_standby(
                item["clave"],
                float(item["horas"]),
                int(item.get("cantidad", 1)),
                queda_conectado=bool(item.get("queda_conectado", True)),
                veces_semana=float(item.get("veces_semana", 7)),
            )
            resultado["tarifa_aplicada"] = tarifa
            desglose.append(resultado)
            total_kwh_mes += resultado["kwh_mes_actual"]
            ahorro_potencial_clp_mes += resultado.get("ahorro_clp_mes", 0)
        except ValueError:
            continue  # clave desconocida, se ignora en vez de romper el cálculo

    # Iluminación (puede haber varios tipos a la vez: LED + fluorescente, etc.)
    for item in datos.get("iluminacion", []):
        try:
            resultado = calculos.consumo_iluminacion(item["tipo"], int(item["cantidad"]), float(item["horas"]))
            desglose.append(resultado)
            total_kwh_mes += resultado["kwh_mes_actual"]
            ahorro_potencial_clp_mes += resultado.get("ahorro_clp_mes", 0)
        except (ValueError, KeyError):
            continue

    # Hervidor de agua
    hervidor = datos.get("hervidor")
    if hervidor and hervidor.get("tiene"):
        resultado = calculos.ahorro_hervidor(
            float(hervidor["litros_habitual"]), float(hervidor["litros_necesario"]), int(hervidor.get("usos_dia", 1))
        )
        resultado["nombre"] = "Hervidor de agua"
        desglose.append(resultado)
        total_kwh_mes += resultado["kwh_mes_llenado_habitual"]
        ahorro_potencial_clp_mes += resultado.get("ahorro_clp_mes", 0)

    # Artefactos personalizados (mueblista, arquitecto, médico, etc.)
    for item in datos.get("personalizados", []):
        resultado = calculos.consumo_personalizado(
            item.get("nombre", "Artefacto personalizado"),
            float(item["watts"]),
            float(item["horas"]),
            cantidad=int(item.get("cantidad", 1)),
        )
        desglose.append(resultado)
        total_kwh_mes += resultado["kwh_mes_actual"]

    total_clp_mes = calculos.kwh_a_clp(total_kwh_mes, tarifa)

    resumen = {
        "total_kwh_mes": round(total_kwh_mes, 2),
        "total_clp_mes": round(total_clp_mes, 0),
        "ahorro_potencial_clp_mes": round(ahorro_potencial_clp_mes, 0),
        "desglose": desglose,
        "recomendaciones": generar_recomendaciones(desglose),
        "proyeccion": {
            "ahorro_1_mes": round(ahorro_potencial_clp_mes, 0),
            "ahorro_6_meses": round(ahorro_potencial_clp_mes * 6, 0),
            "ahorro_1_anio": round(ahorro_potencial_clp_mes * 12, 0),
            "ahorro_5_anios": round(ahorro_potencial_clp_mes * 60, 0),
        },
    }

    resumen["narrativa"] = generar_narrativa(resumen)
    return jsonify(resumen)

@app.route("/api/subir-boleta", methods=["POST"])
def subir_boleta():
    """
    Recibe una imagen (PNG/JPG/WEBP) o PDF de la boleta eléctrica.
    - PDF: extrae el texto con pdfplumber y lo analiza con Groq.
    - Imagen: codifica en base64 y usa el modelo de visión de Groq.
    Devuelve: {kwh_mes, tarifa_kwh, moneda, simbolo, confianza, nota}
    """
    if "boleta" not in request.files:
        return jsonify({"error": "No se recibió ningún archivo."}), 400

    archivo = request.files["boleta"]
    pais_codigo = request.form.get("pais", "CL")

    if archivo.filename == "":
        return jsonify({"error": "Nombre de archivo vacío."}), 400

    if not extension_permitida(archivo.filename):
        return jsonify({"error": "Solo se aceptan imágenes (PNG, JPG, WEBP) o PDF."}), 400

    # Guardar temporalmente
    nombre_seguro = secure_filename(archivo.filename)
    ruta_temp = os.path.join(app.config["UPLOAD_FOLDER"], nombre_seguro)
    archivo.save(ruta_temp)

    # Obtener info del país
    datos_pais = calculos.REFERENCIA["paises"].get(pais_codigo, {})
    moneda  = datos_pais.get("moneda",  "local")
    simbolo = datos_pais.get("simbolo", "")
    nombre_pais = datos_pais.get("nombre", "tu país")

    try:
        import json as _json
        extension = nombre_seguro.rsplit(".", 1)[1].lower()
        groq_api_key = os.getenv("GROQ_API_KEY")

        prompt_extraccion = f"""Analiza esta boleta eléctrica de {nombre_pais} (moneda: {moneda}).

Extrae con precisión:
1. El CONSUMO TOTAL en kWh del período facturado (busca: kWh, consumo, energía activa, kwh consumidos).
2. El PRECIO POR kWh en {moneda} (busca: tarifa, precio unitario, costo por kWh, valor kWh).

RESPONDE SOLO con este JSON exacto, sin texto adicional:
{{"kwh_mes": NÚMERO_O_NULL, "tarifa_kwh": NÚMERO_O_NULL, "confianza": "alta|media|baja", "nota": "explicación breve"}}"""

        # ── CASO PDF: extraer texto con pdfplumber ──────────────────
        if extension == "pdf":
            import pdfplumber
            texto_pdf = ""
            with pdfplumber.open(ruta_temp) as pdf:
                for pagina in pdf.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_pdf += texto_pagina + "\n"

            if not texto_pdf.strip():
                return jsonify({
                    "error": "No se pudo extraer texto del PDF. Puede ser un PDF escaneado sin texto. Prueba subiendo una foto (JPG/PNG)."
                }), 422

            # Intentar extraer con regex primero (rápido, sin API)
            kwh_regex   = re.search(r'(\d[\d.,]+)\s*kWh', texto_pdf, re.IGNORECASE)
            tarifa_regex = re.search(
                r'(?:tarifa|precio|costo|valor)\s*(?:por\s*)?kWh[^0-9]*(\d[\d.,]+)',
                texto_pdf, re.IGNORECASE
            )

            kwh_extraido   = float(kwh_regex.group(1).replace(",", "."))   if kwh_regex   else None
            tarifa_extraida = float(tarifa_regex.group(1).replace(",", ".")) if tarifa_regex else None

            # Si no tenemos ambos valores, usar Groq con texto
            if groq_api_key and (kwh_extraido is None or tarifa_extraida is None):
                llm = ChatGroq(
                    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                    temperature=0,
                    api_key=groq_api_key,
                )
                contenido_prompt = f"{prompt_extraccion}\n\nTEXTO DE LA BOLETA:\n{texto_pdf[:4000]}"
                respuesta = llm.invoke([HumanMessage(content=contenido_prompt)])
                texto_resp = respuesta.content.strip()
                match = re.search(r'\{[^{}]+\}', texto_resp, re.DOTALL)
                if match:
                    datos = _json.loads(match.group())
                    kwh_extraido    = datos.get("kwh_mes")    or kwh_extraido
                    tarifa_extraida = datos.get("tarifa_kwh") or tarifa_extraida
                    confianza       = datos.get("confianza",  "media")
                    nota            = datos.get("nota",       "")
                else:
                    confianza, nota = "baja", "Extracción automática parcial."
            else:
                confianza = "alta" if (kwh_extraido and tarifa_extraida) else "media"
                nota = "Datos extraídos del texto del PDF."

            return jsonify({
                "kwh_mes":    kwh_extraido,
                "tarifa_kwh": tarifa_extraida,
                "moneda":     moneda,
                "simbolo":    simbolo,
                "confianza":  confianza,
                "nota":       nota,
            })

        # ── CASO IMAGEN: enviar en base64 al modelo de visión ──────
        if not groq_api_key:
            return jsonify({"error": "Clave API no configurada. Configura GROQ_API_KEY en el archivo .env para analizar imágenes."}), 500

        with open(ruta_temp, "rb") as f:
            imagen_b64 = base64.b64encode(f.read()).decode("utf-8")

        tipo_mime = {
            "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "png": "image/png",  "webp": "image/webp"
        }.get(extension, "image/jpeg")

        llm = ChatGroq(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0,
            api_key=groq_api_key,
        )

        mensaje = HumanMessage(content=[
            {"type": "text",      "text": prompt_extraccion},
            {"type": "image_url", "image_url": {"url": f"data:{tipo_mime};base64,{imagen_b64}"}}
        ])

        respuesta = llm.invoke([mensaje])
        texto = respuesta.content.strip()

        match = re.search(r'\{[^{}]+\}', texto, re.DOTALL)
        if match:
            datos = _json.loads(match.group())
            return jsonify({
                "kwh_mes":    datos.get("kwh_mes"),
                "tarifa_kwh": datos.get("tarifa_kwh"),
                "moneda":     moneda,
                "simbolo":    simbolo,
                "confianza":  datos.get("confianza", "media"),
                "nota":       datos.get("nota", ""),
            })
        else:
            return jsonify({"error": "No se pudieron extraer datos de la imagen.", "texto_extraido": texto}), 422

    except Exception as e:
        return jsonify({"error": f"Error al procesar la boleta: {str(e)}"}), 500
    finally:
        if os.path.exists(ruta_temp):
            os.remove(ruta_temp)


@app.route("/api/analisis-energetico", methods=["POST"])
def analisis_energetico_mvp():
    data = request.get_json(force=True) or {}
    
    # 1. Leer las 5 variables requeridas por el Hackathon
    consumo = float(data.get("consumo_kwh", 0))
    uso_pico = bool(data.get("uso_horario_pico", False))
    cantidad_equipos = int(data.get("cantidad_equipos", 1))
    tipo_inmueble = data.get("tipo_inmueble", "Casa")
    horas_alto_consumo = int(data.get("horas_alto_consumo", 0))

    # 2. Regla financiera obligatoria del Hackathon ($0.75 USD por kWh)
    costo_estimado = round(consumo * 0.75, 2)

    # 3. Clasificación base (Mock mientras el equipo de ML sube su modelo .pkl)
    if consumo > 350 or uso_pico or horas_alto_consumo > 6:
        categoria = "Ineficiente"
        probabilidad = 0.81
        recomendaciones = [
            "Reducir el uso de equipos durante los horarios pico",
            "Evaluar equipos con alto consumo energético (más de 1000W)",
            "Distribuir las actividades de mayor consumo a lo largo del día",
            "Desconectar cargadores y artefactos en stand-by"
        ]
    elif consumo > 200:
        categoria = "Moderado"
        probabilidad = 0.75
        recomendaciones = [
            "Reemplazar luminarias por tecnología LED eficientes",
            "Evitar llenar el hervidor de agua completo si solo usarás una taza"
        ]
    else:
        categoria = "Eficiente"
        probabilidad = 0.92
        recomendaciones = [
            "¡Excelente hábito de consumo! Mantén tus equipos desenchufados",
            "Aprovecha la luz natural durante el día"
        ]

    # 4. JSON de respuesta unificado
    return jsonify({
        "categoria": categoria,
        "probabilidad": probabilidad,
        "costo_estimado_mensual": costo_estimado,
        "recomendaciones": recomendaciones
    })

if __name__ == "__main__":
    puerto = int(os.getenv("PORT", 5000))
    modo_debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=puerto, debug=modo_debug)