"""
Agente asesor energético.

Persona: bot cercano y con humor ("Bot Chistoso") que hace de asesor
energético. Conversa con el usuario, identifica sus artefactos e
iluminación, y usa herramientas de cálculo determinístico (nunca
calcula a mano) para estimar consumo y ahorro potencial.
"""
import json
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from src.tools import HERRAMIENTAS

load_dotenv()

SYSTEM_PROMPT = """Eres "Vóltico", un asesor energético con buen humor que ayuda a personas en Chile a entender y reducir su consumo eléctrico.

Tu forma de trabajar:
1. Saluda con calidez y algo de humor breve, y explica en 1-2 frases qué vas a hacer.
2. Haz las preguntas directamente, DE A UNA POR VEZ. 
   
⚠️ REGLAS DIRECTIVAS MANDATORIAS:
- NUNCA le preguntes al usuario si "desea continuar", si "quiere dar más detalles" o si "quiere una información más detallada". 
- NO pidas permiso para seguir preguntando. Pasa a la siguiente pregunta directamente.
- Debes recolectar obligatoriamente estas respuestas en este orden:
  1. Artefactos conectados a la red.
  2. Tipo de iluminación.
  3. Matriz energética para agua caliente.
  4. Uso de secarropas eléctrica.
  5. [TU ÚLTIMA PREGUNTA AQUÍ].

3. NO INVOQUES NINGUNA HERRAMIENTA hasta completar las 5 preguntas anteriores.
4. NUNCA inventes ni calcules tú mismo los números. SIEMPRE usa las herramientas cuando tengas TODAS las respuestas.
5. Cuando tengas resultados de las herramientas, explica el ahorro en kWh y en pesos chilenos (CLP) de forma clara y concreta, con recomendaciones prácticas.
6. Sé breve y directo. Nada de rellenar con paja motivacional.
""" 

def crear_agente():
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        temperature=0.4,
        api_key=os.getenv("GROQ_API_KEY"),
    )
    return llm.bind_tools(HERRAMIENTAS)


def ejecutar_turno(llm_con_tools, historial):
    """
    Ejecuta un turno del agente: llama al modelo, y si pide usar
    herramientas, las ejecuta y vuelve a llamar al modelo con los
    resultados hasta obtener una respuesta final en texto.
    """
    herramientas_por_nombre = {h.name: h for h in HERRAMIENTAS}

    respuesta = llm_con_tools.invoke(historial)
    historial.append(respuesta)

    # Bucle de tool-calling: puede requerir varias llamadas encadenadas
    while respuesta.tool_calls:
        for llamada in respuesta.tool_calls:
            herramienta = herramientas_por_nombre[llamada["name"]]
            resultado = herramienta.invoke(llamada["args"])
            historial.append(
                ToolMessage(content=json.dumps(resultado, ensure_ascii=False), tool_call_id=llamada["id"])
            )
        respuesta = llm_con_tools.invoke(historial)
        historial.append(respuesta)

    return respuesta.content, historial


def main():
    llm_con_tools = crear_agente()
    historial = [SystemMessage(content=SYSTEM_PROMPT)]

    print("Vóltico ⚡ — asesor energético. Escribe 'salir' para terminar.\n")

    # Primer mensaje del bot sin input del usuario
    respuesta, historial = ejecutar_turno(llm_con_tools, historial + [HumanMessage(content="Hola")])
    print(f"Vóltico: {respuesta}\n")

    while True:
        entrada = input("Tú: ").strip()
        if entrada.lower() in ("salir", "exit", "quit"):
            print("Vóltico: ¡Listo! Cuida tu consumo y tu boleta 👋")
            break

        historial.append(HumanMessage(content=entrada))
        respuesta, historial = ejecutar_turno(llm_con_tools, historial)
        print(f"Vóltico: {respuesta}\n")


if __name__ == "__main__":
    main()
