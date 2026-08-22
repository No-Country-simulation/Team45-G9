"""
Mapeo de "provincia/estado" (texto libre, el mismo campo que ya llena Denji
por geolocalización o que el usuario escribe a mano) al código numérico
exacto que usa el modelo de eficiencia energética real de datacience.

Por qué existe esto: el campo de la vivienda siempre fue texto libre a
propósito — la persona no tiene por qué saber ni ver ningún código, y la
geolocalización automática tampoco lo conoce. Este módulo es el único lugar
donde ese texto se traduce a un número; nadie más en el backend ni en el
frontend necesita saber que ese número existe.

Solo aplica a USA y Chile — son los dos únicos países con modelo de
regresión propio (el resto usa un "modelo prestado" sin necesitar este
nivel de detalle geográfico). Para cualquier otro país, mapear_estado()
devuelve None sin fallar.
"""
from __future__ import annotations

import re
import unicodedata

# ── Estados de EE.UU. — código usado por HDD['USA']/CDD['USA'] ─────────────
ESTADOS_USA = {
    1: "Alabama", 2: "Alaska", 3: "Arizona", 4: "Arkansas", 5: "California",
    6: "Colorado", 7: "Connecticut", 8: "Delaware", 9: "District of Columbia",
    10: "Florida", 11: "Georgia", 12: "Hawaii", 13: "Idaho", 14: "Illinois",
    15: "Indiana", 16: "Iowa", 17: "Kansas", 18: "Kentucky", 19: "Louisiana",
    20: "Maine", 21: "Maryland", 22: "Massachusetts", 23: "Michigan",
    24: "Minnesota", 25: "Mississippi", 26: "Missouri", 27: "Montana",
    28: "Nebraska", 29: "Nevada", 30: "New Hampshire", 31: "New Jersey",
    32: "New Mexico", 33: "New York", 34: "North Carolina", 35: "North Dakota",
    36: "Ohio", 37: "Oklahoma", 38: "Oregon", 39: "Pennsylvania",
    40: "Rhode Island", 41: "South Carolina", 42: "South Dakota",
    43: "Tennessee", 44: "Texas", 45: "Utah", 46: "Vermont", 47: "Virginia",
    48: "Washington", 49: "West Virginia", 50: "Wisconsin", 51: "Wyoming",
}
# Abreviaturas de 2 letras — la gente también escribe "CA", "NY", etc.
ABREVIATURAS_USA = {
    "AL": 1, "AK": 2, "AZ": 3, "AR": 4, "CA": 5, "CO": 6, "CT": 7, "DE": 8,
    "DC": 9, "FL": 10, "GA": 11, "HI": 12, "ID": 13, "IL": 14, "IN": 15,
    "IA": 16, "KS": 17, "KY": 18, "LA": 19, "ME": 20, "MD": 21, "MA": 22,
    "MI": 23, "MN": 24, "MS": 25, "MO": 26, "MT": 27, "NE": 28, "NV": 29,
    "NH": 30, "NJ": 31, "NM": 32, "NY": 33, "NC": 34, "ND": 35, "OH": 36,
    "OK": 37, "OR": 38, "PA": 39, "RI": 40, "SC": 41, "SD": 42, "TN": 43,
    "TX": 44, "UT": 45, "VT": 46, "VA": 47, "WA": 48, "WV": 49, "WI": 50,
    "WY": 51,
}

# ── Provincias de Chile — código usado por HDD['CHILE']/CDD['CHILE'] ────────
PROVINCIAS_CHILE = {
    1: "Arica", 2: "Parinacota", 3: "Iquique", 4: "Tamarugal",
    5: "Antofagasta", 6: "El Loa", 7: "Tocopilla", 8: "Copiapó",
    9: "Chañaral", 10: "Huasco", 11: "Elqui", 12: "Limarí", 13: "Choapa",
    14: "Valparaíso", 15: "Isla de Pascua", 16: "Los Andes", 17: "Petorca",
    18: "Quillota", 19: "San Antonio", 20: "San Felipe de Aconcagua",
    21: "Marga Marga", 22: "Santiago", 23: "Cordillera", 24: "Chacabuco",
    25: "Maipo", 26: "Melipilla", 27: "Talagante", 28: "Cachapoal",
    29: "Colchagua", 30: "Cardenal Caro", 31: "Curicó", 32: "Talca",
    33: "Linares", 34: "Cauquenes", 35: "Diguillín", 36: "Itata",
    37: "Punilla", 38: "Concepción", 39: "Arauco", 40: "Biobío",
    41: "Cautín", 42: "Malleco", 43: "Valdivia", 44: "Ranco",
    45: "Llanquihue", 46: "Chiloé", 47: "Osorno", 48: "Palena",
    49: "Coyhaique", 50: "Aysén", 51: "General Carrera", 52: "Capitán Prat",
    53: "Magallanes", 54: "Última Esperanza", 55: "Tierra del Fuego",
    56: "Antártica Chilena",
}
# La geolocalización (Nominatim) da la REGIÓN, no la provincia — más ancha.
# Si solo tenemos el nombre de la región, se usa la provincia "capital" de
# esa región (la primera que aparece agrupada bajo ella) como representante.
REGIONES_CHILE_A_PROVINCIA_REPRESENTANTE = {
    "Arica y Parinacota": 1, "Tarapacá": 3, "Antofagasta": 5, "Atacama": 8,
    "Coquimbo": 11, "Valparaíso": 14, "Metropolitana de Santiago": 22,
    "Región Metropolitana": 22, "O'Higgins": 28,
    "Libertador General Bernardo O'Higgins": 28, "Maule": 31, "Ñuble": 35,
    "Biobío": 38, "La Araucanía": 41, "Los Ríos": 43, "Los Lagos": 45,
    "Aysén": 49, "Aysén del General Carlos Ibáñez del Campo": 49,
    "Magallanes": 53, "Magallanes y de la Antártica Chilena": 53,
}

_CODIGOS_POR_PAIS = {"US": (ESTADOS_USA, ABREVIATURAS_USA), "CL": (PROVINCIAS_CHILE, None)}


def _normalizar(texto: str) -> str:
    """minúsculas, sin acentos, sin espacios/puntuación extra — para que
    'Región del Libertador Bernardo O'Higgins' y 'ohiggins' calcen igual."""
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = texto.lower().strip()
    texto = texto.replace("'", "").replace("’", "")  # antes del regex: sin espacio de por medio
    texto = re.sub(r"[^a-z0-9]+", " ", texto).strip()
    return texto


def mapear_estado(pais_iso: str, texto_estado: str) -> int | None:
    """Devuelve el código numérico exacto (1-51 para USA, 1-56 para Chile)
    que corresponde al texto libre recibido, o None si no se pudo reconocer
    o el país no es USA/Chile (los dos únicos con modelo propio).

    Nunca lanza — un texto irreconocible simplemente no tiene código, y el
    resto de la app sigue funcionando igual (solo el score de eficiencia
    queda sin ese nivel de detalle geográfico para ese caso puntual).
    """
    pais_iso = (pais_iso or "").upper()
    if pais_iso not in _CODIGOS_POR_PAIS or not texto_estado:
        return None

    nombres, abreviaturas = _CODIGOS_POR_PAIS[pais_iso]
    texto_norm = _normalizar(texto_estado)

    # 1) Coincidencia exacta contra el nombre oficial (provincia o estado)
    for codigo, nombre in nombres.items():
        if _normalizar(nombre) == texto_norm:
            return codigo

    # 2) Abreviatura de 2 letras (solo USA: "CA", "ny", etc.)
    if abreviaturas and texto_estado.strip().upper() in abreviaturas:
        return abreviaturas[texto_estado.strip().upper()]

    # 3) Nombre de región de Chile (lo que da la geolocalización), mapeado a
    #    la provincia representante de esa región.
    if pais_iso == "CL":
        for region, codigo in REGIONES_CHILE_A_PROVINCIA_REPRESENTANTE.items():
            if _normalizar(region) == texto_norm:
                return codigo

    # 4) Coincidencia parcial — el texto contiene el nombre, o viceversa
    #    (ej. "Provincia de Santiago" contiene "santiago"; "santiag" es
    #    substring de "santiago" solo si el usuario tipeó incompleto — acá
    #    se prioriza no confundir provincias distintas con nombres parecidos,
    #    por eso se exige que uno contenga completo al otro, no una porción).
    for codigo, nombre in nombres.items():
        nombre_norm = _normalizar(nombre)
        if nombre_norm in texto_norm or texto_norm in nombre_norm:
            return codigo
    if pais_iso == "CL":
        for region, codigo in REGIONES_CHILE_A_PROVINCIA_REPRESENTANTE.items():
            region_norm = _normalizar(region)
            if region_norm in texto_norm or texto_norm in region_norm:
                return codigo

    return None
