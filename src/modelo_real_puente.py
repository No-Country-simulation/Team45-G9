"""
Puente entre nuestro payload (el que llena el wizard) y el modelo real de
eficiencia energética de datacience (src/modelo_real_datacience.py).

Por qué existe este módulo separado: el modelo real espera nombres de campo
distintos a los nuestros (tv_cantidad en vez de tv, lavarropas_frecuencia en
vez de lavado_frecuencia, etc.) y códigos numéricos de país/estado que
nuestro wizard nunca expone al usuario. Acá vive toda esa traducción, en un
solo lugar — ni el frontend ni el resto del backend necesitan saber que
estos códigos existen.

Degradación: si el país no está en las 35 que soporta el modelo real, o si
algo falla al calcular, se devuelve None — quien llama (src/modelo.py) cae
al cálculo por percentil que ya existía, sin romper nada.
"""
from __future__ import annotations

import logging

from src import geo_codigos
from src.modelo_real_datacience import predecir_eficiencia_real

logger = logging.getLogger("denji.modelo_real")

# ISO-2 (el código que ya usamos en toda la app) -> nombre exacto que usa
# PAISES en el modelo real. Los países que no aparecen acá (España, Puerto
# Rico) no están en las 35 que soporta el modelo real — degradan solo.
ISO2_A_NOMBRE_MODELO_REAL = {
    "CA": "CANADA", "US": "USA", "MX": "MEXICO", "BZ": "BELIZE",
    "CR": "COSTA RICA", "SV": "EL SALVADOR", "GT": "GUATEMALA",
    "HN": "HONDURAS", "NI": "NICARAGUA", "PA": "PANAMA",
    "CU": "CUBA", "DO": "DOMINICAN REPUBLIC", "HT": "HAITI", "JM": "JAMAICA",
    "AR": "ARGENTINA", "BO": "BOLIVIA", "BR": "BRAZIL", "CL": "CHILE",
    "CO": "COLOMBIA", "EC": "ECUADOR", "PY": "PARAGUAY", "PE": "PERU",
    "UY": "URUGUAY", "VE": "VENEZUELA",
}
# Nombre (como en PAISES) -> código numérico, derivado de src/modelo_real_datacience.py
NOMBRE_A_CODIGO_PAIS = {
    "CANADA": 1, "USA": 2, "MEXICO": 3, "BELIZE": 4, "COSTA RICA": 5,
    "EL SALVADOR": 6, "GUATEMALA": 7, "HONDURAS": 8, "NICARAGUA": 9,
    "PANAMA": 10, "ANTIGUA AND BARBUDA": 11, "BAHAMAS": 12, "BARBADOS": 13,
    "CUBA": 14, "DOMINICA": 15, "DOMINICAN REPUBLIC": 16, "GRENADA": 17,
    "HAITI": 18, "JAMAICA": 19, "SAINT KITTS AND NEVIS": 20,
    "SAINT LUCIA": 21, "SAINT VINCENT AND THE GRENADINES": 22,
    "TRINIDAD AND TOBAGO": 23, "ARGENTINA": 24, "BOLIVIA": 25, "BRAZIL": 26,
    "CHILE": 27, "COLOMBIA": 28, "ECUADOR": 29, "GUYANA": 30,
    "PARAGUAY": 31, "PERU": 32, "SURINAME": 33, "URUGUAY": 34,
    "VENEZUELA": 35,
}
# Código de estado a usar cuando no se pudo mapear provincia/estado y el
# país sí es USA/Chile (necesitan un estado numérico sí o sí) — el más
# poblado de cada uno, como aproximación razonable, no arbitraria.
ESTADO_POR_DEFECTO = {"US": 5, "CL": 22}  # California, Santiago


def _codigo_pais(pais_iso: str) -> int | None:
    nombre = ISO2_A_NOMBRE_MODELO_REAL.get((pais_iso or "").upper())
    if nombre is None:
        return None
    return NOMBRE_A_CODIGO_PAIS.get(nombre)


def _construir_obs(d: dict, consumo_kwh: float) -> dict | None:
    """Arma el `obs` que espera el modelo real, o None si el país no está
    soportado."""
    codigo_pais = _codigo_pais(d.get("pais", ""))
    if codigo_pais is None:
        return None

    pais_iso = (d.get("pais") or "").upper()
    codigo_estado = geo_codigos.mapear_estado(pais_iso, d.get("estado_provincia", ""))
    if codigo_estado is None:
        codigo_estado = ESTADO_POR_DEFECTO.get(pais_iso, 1)

    return {
        "pais": codigo_pais,
        "estado": codigo_estado,
        "dormitorios": d.get("dormitorios", 0),
        "ventanas": d.get("ventanas", 0),
        "habitantes_mayores": d.get("habitantes_mayores", 0),
        "habitantes_menores": d.get("habitantes_menores", 0),
        "aire_acondicionado": d.get("aire_acondicionado", 0),
        "calefaccion_electrica": d.get("calefaccion_electrica", 0),
        "agua_caliente_electrica": d.get("agua_caliente_electrica", 0),
        # No recolectados hoy en el wizard (ver docs/PLAN-HACKATHON.md) — se
        # asumen 0 (calentador eléctrico estándar, no a gas por galones).
        "agua_caliente_tamano": 0,
        "flag_galones": 0,
        "secarropas_electrico": d.get("secarropas_electrico", 0),
        "horno_electrico": d.get("horno_electrico", 0),
        "refrigerador": d.get("refrigerador", 0),
        "freezer": d.get("freezer", 0),
        "tv_cantidad": d.get("tv", 0),
        "tv_frecuencia": d.get("tv_frecuencia", 0),
        "lavarropas_frecuencia": d.get("lavado_frecuencia", 0),
        "luces_exterior": d.get("luces_exterior", 0),
        "luces_interior_4_horas": d.get("luces_interior", 0),
        "kwh": consumo_kwh,
        "periodo_anual": 0,  # nuestro consumo_kwh siempre es mensual
    }


def calcular(d: dict, consumo_kwh: float) -> dict | None:
    """Devuelve el resultado completo del modelo real, o None si el país no
    está soportado o algo falló — nunca lanza, quien llama debe tener su
    propio respaldo."""
    obs = _construir_obs(d, consumo_kwh)
    if obs is None:
        return None
    try:
        return predecir_eficiencia_real(obs)
    except Exception:
        logger.exception("modelo_real: falló el cálculo, se usa el respaldo por percentil")
        return None
