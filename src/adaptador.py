"""
Capa adaptadora entre el frontend (app.js v9.0 - VólticvS) y el nuevo
motor de calculo Modelo.py (modelo estadistico por pais).

Uso en app.py:

    from adaptador import payload_a_obs, resultado_a_frontend
    from modelo import predecir  # tu Modelo.py ya convertido a funcion

    @app.post("/api/analisis-energetico")
    def analisis_energetico(payload: dict):
        obs = payload_a_obs(payload)
        result = predecir(obs)
        return resultado_a_frontend(result, payload)
"""

# Mapea el codigo ISO-2 que manda el <select id="pais"> del frontend
# al codigo numerico que usa el diccionario PAISES de Modelo.py.
# (Reconstruido a partir del propio diccionario PAISES de Modelo.py)
ISO_A_PAIS_MODELO = {
    "CA": 1,   # CANADA
    "US": 2,   # USA
    "MX": 3,   # MEXICO
    "BZ": 4,   # BELIZE
    "CR": 5,   # COSTA RICA
    "SV": 6,   # EL SALVADOR
    "GT": 7,   # GUATEMALA
    "HN": 8,   # HONDURAS
    "NI": 9,   # NICARAGUA
    "PA": 10,  # PANAMA
    "AG": 11,  # ANTIGUA AND BARBUDA
    "BS": 12,  # BAHAMAS
    "BB": 13,  # BARBADOS
    "CU": 14,  # CUBA
    "DM": 15,  # DOMINICA
    "DO": 16,  # DOMINICAN REPUBLIC
    "GD": 17,  # GRENADA
    "HT": 18,  # HAITI
    "JM": 19,  # JAMAICA
    "KN": 20,  # SAINT KITTS AND NEVIS
    "LC": 21,  # SAINT LUCIA
    "VC": 22,  # SAINT VINCENT AND THE GRENADINES
    "TT": 23,  # TRINIDAD AND TOBAGO
    "AR": 24,  # ARGENTINA
    "BO": 25,  # BOLIVIA
    "BR": 26,  # BRAZIL
    "CL": 27,  # CHILE
    "CO": 28,  # COLOMBIA
    "EC": 29,  # ECUADOR
    "GY": 30,  # GUYANA
    "PY": 31,  # PARAGUAY
    "PE": 32,  # PERU
    "SR": 33,  # SURINAME
    "UY": 34,  # URUGUAY
    "VE": 35,  # VENEZUELA
}

# TODO: completar cuando sepamos que valor manda <select id="selectProvincia">
# (para el wizard) o que texto suelta el usuario en el chat (para el agente).
# Debe traducir ese valor (nombre, sigla, lo que sea) al numero 1..51 (USA)
# o 1..56 (CHILE) que usan los diccionarios HDD['USA'] / HDD['CHILE'] en
# Modelo.py (los nombres de cada numero estan comentados ahi mismo).
# Si el pais no es USA ni CHILE, "estado" no se usa (Modelo.py cae al
# HDD/CDD del pais completo), asi que puede ir en None sin problema.
ESTADO_PROVINCIA_A_NUMERO = {
    # "USA": {"California": 5, "Texas": 44, ...},
    # "CHILE": {"Metropolitana": 22, "Valparaiso": 14, ...},
}

# Nombre legible por codigo ISO-2, para listar paises al agente conversacional.
NOMBRE_PAIS_POR_ISO = {
    "CA": "Canada", "US": "Estados Unidos", "MX": "Mexico", "BZ": "Belice",
    "CR": "Costa Rica", "SV": "El Salvador", "GT": "Guatemala", "HN": "Honduras",
    "NI": "Nicaragua", "PA": "Panama", "AG": "Antigua y Barbuda", "BS": "Bahamas",
    "BB": "Barbados", "CU": "Cuba", "DM": "Dominica", "DO": "Republica Dominicana",
    "GD": "Granada", "HT": "Haiti", "JM": "Jamaica", "KN": "San Cristobal y Nieves",
    "LC": "Santa Lucia", "VC": "San Vicente y las Granadinas", "TT": "Trinidad y Tobago",
    "AR": "Argentina", "BO": "Bolivia", "BR": "Brasil", "CL": "Chile",
    "CO": "Colombia", "EC": "Ecuador", "GY": "Guyana", "PY": "Paraguay",
    "PE": "Peru", "SR": "Surinam", "UY": "Uruguay", "VE": "Venezuela",
}


def estado_a_numero(pais_iso: str, estado_texto: str) -> int:
    """Traduce un estado/region en texto al numero que espera Modelo.py.
    Devuelve 1 (valor por defecto) si el pais no es USA/CHILE, si no se
    mando texto, o si el texto no calza con nada en la tabla (TODO arriba)."""
    pais_num = ISO_A_PAIS_MODELO.get(pais_iso, 27)
    nombre_pais = {2: "USA", 27: "CHILE"}.get(pais_num)
    if not nombre_pais or not estado_texto:
        return 1
    return ESTADO_PROVINCIA_A_NUMERO.get(nombre_pais, {}).get(estado_texto, 1)


def _num(payload: dict, key: str, default: float = 0.0) -> float:
    v = payload.get(key)
    if v in (None, "", False):
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def estimar_kwh_mensual_desde_electrodomesticos(payload: dict) -> float:
    """Estimación de respaldo (heurística, no viene de Modelo.py) para cuando
    el usuario no declaró su consumo de boleta. Modelo.py NO estima consumo
    por su cuenta -- siempre usa el kwh que se le pase tal cual -- así que si
    no hay dato declarado, hay que dárselo ya calculado desde acá.

    Mismos supuestos que usaba la versión anterior de app.py (_estimar_consumo),
    reutilizados aquí para no inventar números nuevos.
    """
    total = 0.0
    total += _num(payload, "habitantes_mayores") * 30
    total += _num(payload, "habitantes_menores") * 15
    total += _num(payload, "aire_acondicionado") * 120
    total += _num(payload, "calefaccion_electrica") * 150
    total += _num(payload, "agua_caliente_electrica") * 180
    total += _num(payload, "secarropas_electrico") * 40
    total += _num(payload, "horno_electrico") * 30
    total += _num(payload, "refrigerador") * 35
    total += _num(payload, "freezer") * 45
    total += _num(payload, "tv") * _num(payload, "tv_frecuencia") * 0.1 * 4.33
    total += _num(payload, "lavado_frecuencia") * 3.5 * 4.33

    return round(total, 1) if total > 0 else 50.0  # mínimo plausible, igual que antes


def payload_a_obs(payload: dict) -> dict:
    """Convierte el JSON que manda app.js al formato 'obs' que espera Modelo.py."""

    pais_iso = (payload.get("pais") or "CL").upper()
    pais_num = ISO_A_PAIS_MODELO.get(pais_iso, 27)  # 27 = CHILE por defecto

    # Averigua a que nombre de pais (para el mapa de estado/region) corresponde
    nombre_pais = {2: "USA", 27: "CHILE"}.get(pais_num)
    estado_num = 1  # valor por defecto si no aplica o no se pudo mapear
    if nombre_pais:
        tabla = ESTADO_PROVINCIA_A_NUMERO.get(nombre_pais, {})
        estado_num = tabla.get(payload.get("estado_provincia"), 1)

    # kwh declarado por el usuario (de su boleta). Si no lo puso (0/vacio),
    # se usa una estimacion de respaldo a partir de los electrodomesticos,
    # y esa estimacion siempre es MENSUAL -> periodo_anual=0 para que
    # Modelo.py la multiplique por 12 y quede consistente.
    kwh_declarado = _num(payload, "consumo_kwh") or _num(payload, "consumo")
    if kwh_declarado > 0:
        kwh_final = kwh_declarado
        periodo_anual_final = payload.get("flag_anual", 1)
        fuente_kwh = "declarado"
    else:
        kwh_final = estimar_kwh_mensual_desde_electrodomesticos(payload)
        periodo_anual_final = 0
        fuente_kwh = "estimado"

    return {
        "pais": pais_num,
        "estado": estado_num,
        "dormitorios": payload.get("dormitorios", 0),
        "ventanas": payload.get("ventanas", 0),
        "habitantes_mayores": payload.get("habitantes_mayores", 0),
        "habitantes_menores": payload.get("habitantes_menores", 0),
        "agua_caliente_electrica": payload.get("agua_caliente_electrica", 0),
        "agua_caliente_tamano": payload.get("agua_caliente_tamano", 0),
        "flag_galones": payload.get("flag_galones", 1),
        "calefaccion_electrica": payload.get("calefaccion_electrica", 0),
        "horno_electrico": payload.get("horno_electrico", 0),
        # nombre distinto en el frontend:
        "lavarropas_frecuencia": payload.get("lavado_frecuencia", 0),
        "secarropas_electrico": payload.get("secarropas_electrico", 0),
        "aire_acondicionado": payload.get("aire_acondicionado", 0),
        # nombre distinto en el frontend:
        "tv_cantidad": payload.get("tv", 0),
        "tv_frecuencia": payload.get("tv_frecuencia", 0),
        "freezer": payload.get("freezer", 0),
        "refrigerador": payload.get("refrigerador", 0),
        "luces_exterior": payload.get("luces_exterior", 0),
        # nombre distinto en el frontend:
        "luces_interior_4_horas": payload.get("luces_interior", 0),
        "kwh": kwh_final,
        "periodo_anual": periodo_anual_final,
        # no lo usa Modelo.py, pero resultado_a_frontend lo puede leer para
        # mostrar "estimado" vs "declarado" en fuente_consumo:
        "_fuente_kwh": fuente_kwh,
    }


def resultado_a_frontend(result: dict, payload: dict) -> dict:
    """Convierte la salida de Modelo.py al shape que espera analisis_energetico_mvp()
    en app.py (Flask) y mostrarResultados() en app.js.

    Decisiones tomadas:
    - Todo en USD (Modelo.py calcula en USD via PRECIO_KWH_PAIS; se deja de
      usar _TARIFAS/moneda local para este endpoint).
    - Cifras en base MENSUAL para no romper la consistencia con lo que el
      frontend ya mostraba (Modelo.py calcula todo en base anual).
    - ahorro_estimado: Modelo.py NO devuelve un ahorro en $ real (solo
      recomendaciones en texto). Se mantiene el mismo heuristico que ya
      usaba app.py (20% del costo estimado) hasta que se defina un calculo
      real. Buscar "TODO ahorro_estimado" para encontrar este punto despues.
    """
    salida = result["salida"]
    financiero = result["estimacion_financiera"]
    complementaria = result["salida_complementaria"]

    consumo_kwh_mes = round(salida["Consumo (KWH anual)"] / 12, 1)
    costo_estimado = round(financiero["Gastos estimados en dolares (mensual)"], 2)
    # TODO ahorro_estimado: heuristico temporal, ver docstring arriba
    ahorro_estimado = round(costo_estimado * 0.20, 2)
    categoria = salida["Perfil de eficiencia"]  # Muy eficiente..Muy ineficiente
    kwh_declarado = _num(payload, "consumo_kwh") or _num(payload, "consumo")
    fuente_consumo = "declarado" if kwh_declarado > 0 else "estimado"

    return {
        "status": "success",
        "consumo_kwh": consumo_kwh_mes,
        "costo_estimado": costo_estimado,
        "ahorro_estimado": ahorro_estimado,
        "simbolo_moneda": "$",
        "moneda": "USD",
        "categoria": categoria,
        "fuente_consumo": fuente_consumo,
        "desglose": {
            "Agua caliente sanitaria (%)": salida["Consumo en calentar agua sanitaria (porcentaje)"],
            "Aire acondicionado (%)": salida["Consumo en aire acondicionado (porcentaje)"],
            "Calefacción (%)": salida["Consumo en calefaccion (porcentaje)"],
            "Cocina (%)": salida["Consumo en cocina (porcentaje)"],
            "Refrigeración (%)": salida["Consumo en refrigeracion (porcentaje)"],
            "Lavado (%)": salida["Consumo en lavado (porcentaje)"],
            "Iluminación (%)": salida["Consumo en iluminacion (porcentaje)"],
            "Televisión (%)": salida["Consumo en television (porcentaje)"],
            "Otros (%)": salida["Consumo en otros (porcentaje)"],
        },
        "recomendaciones": complementaria["recomendaciones"],
        "narrativa": None,  # se completa en app.py con generar_narrativa()
        # Aliases de compatibilidad que ya usaba la respuesta anterior:
        "costo_estimado_mensual": costo_estimado,
        "total_kwh_mes": consumo_kwh_mes,
        "total_clp_mes": costo_estimado,
        "ahorro_potencial_clp_mes": ahorro_estimado,
        "probabilidad": round(result["salida"]["Probabilidad"], 2),
        "advertencias": complementaria["advertencias"],
        "ranking": salida["Ranking"],
        "ranking_interpretacion": salida["Ranking interpretacion"],
    }    