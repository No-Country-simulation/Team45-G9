"""
Motor de calculo energetico -- modelo estadistico por pais.
Convertido desde el script original Modelo.py: la logica que antes
corria una vez por archivo (leyendo INPUT.json y escribiendo OUTPUT.json)
ahora vive en la funcion predecir(obs), reutilizable desde app.py y
desde las tools de LangChain.
"""
import json
import numpy as np
import pandas as pd
from scipy import stats

'''
obs = {
    "pais" : 2,
    "estado" : 10,
    "dormitorios" : 1,
    "tamano": 500,
    "ventanas": 2,
    "habitantes_mayores": 2,
    "habitantes_menores": 0,
    "agua_caliente_electrica":0,
    "agua_caliente_tamano": 30,
    "flag_galones": 1,
    "calefaccion_electrica" : 0,
    "horno_electrico" : 0,
    "lavarropas_frecuencia" : 7,
    "secarropas_electrico" : 0,
    "aire_acondicionado" : 1,
    "tv_cantidad" : 1,
    "tv_frecuencia": 10,
    "freezer" : 0,
    "refrigerador": 1,
    "luces_exterior":0,
    "luces_interior_4_horas": 3,
    "kwh": 2000,
    "periodo_anual": 1



}
'''

# PRECIOS
PRECIO_KWH_PAIS = {
    "CANADA": 0.123,
    "USA": 0.188,
    "MEXICO": 0.109,
    "BELIZE": 0.219,
    "COSTA RICA": 0.170,
    "EL SALVADOR": 0.254,
    "GUATEMALA": 0.299,
    "HONDURAS": 0.231,
    "NICARAGUA": 0.176,
    "PANAMA": 0.176,
    "ANTIGUA AND BARBUDA": 0.75,#
    "BAHAMAS": 0.348,
    "BARBADOS": 0.314,
    "CUBA": 0.014,
    "DOMINICA":  0.75,#
    "DOMINICAN REPUBLIC": 0.115,
    "GRENADA":  0.75,#
    "HAITI":  0.75,#
    "JAMAICA": 0.290,
    "SAINT KITTS AND NEVIS":  0.75,#
    "SAINT LUCIA":  0.75,#
    "SAINT VINCENT AND THE GRENADINES":  0.75,#
    "TRINIDAD AND TOBAGO": 0.057,
    "ARGENTINA": 0.087,
    "BOLIVIA": 0.75,
    "BRAZIL": 0.164,
    "CHILE": 0.228,
    "COLOMBIA": 0.207,
    "ECUADOR": 0.097,
    "GUYANA": 0.75,#
    "PARAGUAY": 0.055,
    "PERU": 0.186,
    "SURINAME": 0.050,
    "URUGUAY": 0.255,
    "VENEZUELA": 0.069
}
#### Paises


PAISES = {
  1: "CANADA",
  2: "USA",
  3: "MEXICO",
  4: "BELIZE",
  5: "COSTA RICA",
  6: "EL SALVADOR",
  7: "GUATEMALA",
  8: "HONDURAS",
  9: "NICARAGUA",
  10: "PANAMA",
  11: "ANTIGUA AND BARBUDA",
  12: "BAHAMAS",
  13: "BARBADOS",
  14: "CUBA",
  15: "DOMINICA",
  16: "DOMINICAN REPUBLIC",
  17: "GRENADA",
  18: "HAITI",
  19: "JAMAICA",
  20: "SAINT KITTS AND NEVIS",
  21: "SAINT LUCIA",
  22: "SAINT VINCENT AND THE GRENADINES",
  23: "TRINIDAD AND TOBAGO",
  24: "ARGENTINA",
  25: "BOLIVIA",
  26: "BRAZIL",
  27: "CHILE",
  28: "COLOMBIA",
  29: "ECUADOR",
  30: "GUYANA",
  31: "PARAGUAY",
  32: "PERU",
  33: "SURINAME",
  34: "URUGUAY",
  35: "VENEZUELA"
}















# HDD
HDD = {}
# Para los paises que no se tienen datos de HDD, se asigna un valor promedio del pais, fuente banco mundial, año 2024
HDD = {
    "CANADA": 7420*9/5, #convertido a grados Fahrenheit para el modelo usa
    "MEXICO": 404,
    "BELIZE": 0,
    "COSTA RICA": 22,
    "EL SALVADOR": 0,
    "GUATEMALA": 67,
    "HONDURAS": 5,
    "NICARAGUA": 0,
    "PANAMA": 1,
    "ANTIGUA AND BARBUDA": 0,
    "BAHAMAS": 0,
    "BARBADOS": 0,
    "CUBA": 1,
    "DOMINICA": 0,
    "DOMINICAN REPUBLIC": 2,
    "GRENADA": 0,
    "HAITI": 0,
    "JAMAICA": 0,
    "SAINT KITTS AND NEVIS": 0,
    "SAINT LUCIA": 0,
    "SAINT VINCENT AND THE GRENADINES": 0,
    "TRINIDAD AND TOBAGO": 0,
    "ARGENTINA": 1951,
    "BOLIVIA": 816,
    "BRAZIL": 42,
    "CHILE": 3389,
    "COLOMBIA": 105,
    "ECUADOR": 428,
    "GUYANA": 0,
    "PARAGUAY": 221,
    "PERU": 1018,
    "SURINAME": 0,
    "URUGUAY": 990,
    "VENEZUELA": 0
}





# 1 de julio de 2024 a 30 de junio de 2025
# fuente https://ftp.cpc.ncep.noaa.gov/htdocs/products/analysis_monitoring/cdus/degree_days/archives/Heating%20degree%20Days/monthly%20states/2025/Jan%202025.txt
HDD['USA'] = {
    1: 2427,  # AL - Alabama
    2: 9892,  # AK - Alaska
    3: 2058,  # AZ - Arizona
    4: 3098,  # AR - Arkansas
    5: 2421,  # CA - California
    6: 6452,  # CO - Colorado
    7: 5603,  # CT - Connecticut
    8: 4353,  # DE - Delaware
    9: 3325,  # DC - District of Columbia
    10: 593,  # FL - Florida
    11: 2592,  # GA - Georgia
    12: 0,  # HI - Hawaii
    13: 6576,  # ID - Idaho
    14: 5736,  # IL - Illinois
    15: 5412,  # IN - Indiana
    16: 6498,  # IA - Iowa
    17: 4964,  # KS - Kansas
    18: 4096,  # KY - Kentucky
    19: 1762,  # LA - Louisiana
    20: 7400,  # ME - Maine
    21: 4413,  # MD - Maryland
    22: 6014,  # MA - Massachusetts
    23: 6386,  # MI - Michigan
    24: 7809,  # MN - Minnesota
    25: 2199,  # MS - Mississippi
    26: 4749,  # MO - Missouri
    27: 7793,  # MT - Montana
    28: 5836,  # NE - Nebraska
    29: 3490,  # NV - Nevada
    30: 7110,  # NH - New Hampshire
    31: 4979,  # NJ - New Jersey
    32: 4436,  # NM - New Mexico
    33: 5350,  # NY - New York
    34: 3320,  # NC - North Carolina
    35: 8761,  # ND - North Dakota
    36: 5475,  # OH - Ohio
    37: 3418,  # OK - Oklahoma
    38: 5255,  # OR - Oregon
    39: 5619,  # PA - Pennsylvania
    40: 5781,  # RI - Rhode Island
    41: 2571,  # SC - South Carolina
    42: 7157,  # SD - South Dakota
    43: 3613,  # TN - Tennessee
    44: 1590,  # TX - Texas
    45: 6136,  # UT - Utah
    46: 7794,  # VT - Vermont
    47: 4037,  # VA - Virginia
    48: 5602,  # WA - Washington
    49: 4781,  # WV - West Virginia
    50: 7145,  # WI - Wisconsin
    51: 7465,  # WY - Wyoming
}
HDD['CHILE'] = {
    1: 167,    # ARICA
    2: 2803,   # PARINACOTA

    3: 104,    # IQUIQUE
    4: 231,    # TAMARUGAL

    5: 438,    # ANTOFAGASTA
    6: 999,    # EL LOA
    7: 271,    # TOCOPILLA

    8: 909,    # COPIAPÓ
    9: 1001,   # CHAÑARAL
    10: 722,   # HUASCO

    11: 1000,  # ELQUI
    12: 1000,  # LIMARÍ
    13: 1000,  # CHOAPA

    14: 1385,  # VALPARAÍSO
    15: 1385,  # ISLA DE PASCUA
    16: 1385,  # LOS ANDES
    17: 1385,  # PETORCA
    18: 1385,  # QUILLOTA
    19: 1385,  # SAN ANTONIO
    20: 1385,  # SAN FELIPE DE ACONCAGUA
    21: 1385,  # MARGA MARGA

    22: 1011,  # SANTIAGO
    23: 1011,  # CORDILLERA
    24: 1011,  # CHACABUCO
    25: 1011,  # MAIPO
    26: 1011,  # MELIPILLA
    27: 1011,  # TALAGANTE

    28: 1304,  # CACHAPOAL
    29: 1304,  # COLCHAGUA
    30: 1304,  # CARDENAL CARO

    31: 1399,  # CURICÓ
    32: 1399,  # TALCA
    33: 1399,  # LINARES
    34: 1399,  # CAUQUENES

    35: 1603,  # DIGUILLÍN
    36: 1603,  # ITATA
    37: 1603,  # PUNILLA

    38: 1596,  # CONCEPCIÓN
    39: 1596,  # ARAUCO
    40: 1596,  # BIOBÍO

    41: 2062,  # CAUTÍN
    42: 2062,  # MALLECO

    43: 1310,  # VALDIVIA
    44: 1310,  # RANCO

    45: 2140,  # LLANQUIHUE
    46: 2140,  # CHILOÉ
    47: 2140,  # OSORNO
    48: 2140,  # PALENA

    49: 3248,  # COYHAIQUE
    50: 3248,  # AYSÉN
    51: 3248,  # GENERAL CARRERA
    52: 3248,  # CAPITÁN PRAT

    53: 3845,  # MAGALLANES
    54: 3845,  # ÚLTIMA ESPERANZA
    55: 3845,  # TIERRA DEL FUEGO
    56: 3845   # ANTÁRTICA CHILENA
}
# CDD
CDD = {}
# otros paises, fuente banco mundial, año 2024
CDD = {
    "CANADA": 51,
    "UNITED STATES": 666,
    "MEXICO": 1728,
    "BELIZE": 3031,
    "COSTA RICA": 2041,
    "EL SALVADOR": 3090,
    "GUATEMALA": 2217,
    "HONDURAS": 2408,
    "NICARAGUA": 2951,
    "PANAMA": 2715,
    "ANTIGUA AND BARBUDA": 3248,
    "BAHAMAS": 2811,
    "BARBADOS": 3322,
    "CUBA": 2884,
    "DOMINICA": 3102,
    "DOMINICAN REPUBLIC": 2528,
    "GRENADA": 3364,
    "HAITI": 2838,
    "JAMAICA": 3059,
    "SAINT KITTS AND NEVIS": 3239,
    "SAINT LUCIA": 3379,
    "SAINT VINCENT AND THE GRENADINES": 3328,
    "TRINIDAD AND TOBAGO": 3295,
    "ARGENTINA": 846,
    "BOLIVIA": 2003,
    "BRAZIL": 2771,
    "COLOMBIA": 2560,
    "ECUADOR": 1707,
    "GUYANA": 2993,
    "PARAGUAY": 2774,
    "PERU": 1619,
    "SURINAME": 3222,
    "URUGUAY": 700,
    "VENEZUELA": 2560 #imputado por el valor de Colombia
}

CDD['USA'] = {
    1: 2035,  # AL - Alabama
    2: 17,    # AK - Alaska
    3: 2703,  # AZ - Arizona
    4: 1976,  # AR - Arkansas
    5: 818,   # CA - California
    6: 500,   # CO - Colorado
    7: 698,   # CT - Connecticut
    8: 1276,  # DE - Delaware
    9: 1690,  # DC - District of Columbia
    10: 3468, # FL - Florida
    11: 1882, # GA - Georgia
    12: 5034, # HI - Hawaii
    13: 602,  # ID - Idaho
    14: 1093, # IL - Illinois
    15: 1007, # IN - Indiana
    16: 1022, # IA - Iowa
    17: 1360, # KS - Kansas
    18: 1396, # KY - Kentucky
    19: 2719, # LA - Louisiana
    20: 321,  # ME - Maine
    21: 1170, # MD - Maryland
    22: 553,  # MA - Massachusetts
    23: 609,  # MI - Michigan
    24: 646,  # MN - Minnesota
    25: 2457, # MS - Mississippi
    26: 1373, # MO - Missouri
    27: 317,  # MT - Montana
    28: 1096, # NE - Nebraska
    29: 1861, # NV - Nevada
    30: 436,  # NH - New Hampshire
    31: 919,  # NJ - New Jersey
    32: 896,  # NM - New Mexico
    33: 762,  # NY - New York
    34: 1618, # NC - North Carolina
    35: 497,  # ND - North Dakota
    36: 885,  # OH - Ohio
    37: 1895, # OK - Oklahoma
    38: 462,  # OR - Oregon
    39: 780,  # PA - Pennsylvania
    40: 596,  # RI - Rhode Island
    41: 1988, # SC - South Carolina
    42: 829,  # SD - South Dakota
    43: 1540, # TN - Tennessee
    44: 3161, # TX - Texas
    45: 792,  # UT - Utah
    46: 303,  # VT - Vermont
    47: 1296, # VA - Virginia
    48: 369,  # WA - Washington
    49: 1064, # WV - West Virginia
    50: 586,  # WI - Wisconsin
    51: 382,  # WY - Wyoming
}



CDD['CHILE'] = {
    1: 640,    # ARICA
    2: 0,      # PARINACOTA

    3: 616,    # IQUIQUE
    4: 551,    # TAMARUGAL

    5: 407,    # ANTOFAGASTA
    6: 19,     # EL LOA
    7: 510,    # TOCOPILLA

    8: 486,    # COPIAPÓ
    9: 147,    # CHAÑARAL
    10: 317,   # HUASCO

    11: 400,   # ELQUI
    12: 400,   # LIMARÍ
    13: 400,   # CHOAPA

    14: 68,    # VALPARAÍSO
    15: 68,    # ISLA DE PASCUA
    16: 68,    # LOS ANDES
    17: 68,    # PETORCA
    18: 68,    # QUILLOTA
    19: 68,    # SAN ANTONIO
    20: 68,    # SAN FELIPE DE ACONCAGUA
    21: 68,    # MARGA MARGA

    22: 519,   # SANTIAGO
    23: 519,   # CORDILLERA
    24: 519,   # CHACABUCO
    25: 519,   # MAIPO
    26: 519,   # MELIPILLA
    27: 519,   # TALAGANTE

    28: 415,   # CACHAPOAL
    29: 415,   # COLCHAGUA
    30: 415,   # CARDENAL CARO

    31: 495,   # CURICÓ
    32: 495,   # TALCA
    33: 495,   # LINARES
    34: 495,   # CAUQUENES

    35: 328,   # DIGUILLÍN
    36: 328,   # ITATA
    37: 328,   # PUNILLA

    38: 40,    # CONCEPCIÓN
    39: 40,    # ARAUCO
    40: 40,    # BIOBÍO

    41: 52,    # CAUTÍN
    42: 52,    # MALLECO

    43: 377,   # VALDIVIA
    44: 377,   # RANCO

    45: 5,     # LLANQUIHUE
    46: 5,     # CHILOÉ
    47: 5,     # OSORNO
    48: 5,     # PALENA

    49: 3,     # COYHAIQUE
    50: 3,     # AYSÉN
    51: 3,     # GENERAL CARRERA
    52: 3,     # CAPITÁN PRAT

    53: 0,     # MAGALLANES
    54: 0,     # ÚLTIMA ESPERANZA
    55: 0,     # TIERRA DEL FUEGO
    56: 0      # ANTÁRTICA CHILENA
}


#MODELO BASE ---------  

MODELO_BASE = {}

MODELO_BASE['USA'] = {
  'coefs': {
    'const': 2.5929737400729156,
    'CLIMA_grados_dias_enfriamiento_log': 0.09954211071782615,
    'CLIMA_grados_dias_calefaccion_log': 0.0068828117583398934,
    'DORMITORIOS_log': 0.49423717926161864,
    'VENTANAS_log': 0.2980296648011681,
    'HABITANTES_mayores_log': 0.3753245275669875,
    'HABITANTES_menores_log': 0.11633833178520547,
    'AGUA_CALIENTE_electrica': 0.13578276769858272,
    'CALEFACCION_electrico': 0.141543247825371,
    'AIRE_ACONDICIONADO': 0.1496148110403177
  },
 'cov': np.array([
    [ 4.19617993e-03, -7.34061576e-04, -5.24567026e-04, -5.58826254e-05, -3.49010194e-05, -2.57457388e-04, 3.07743337e-05, -3.04906702e-05,  1.91838627e-05, 1.26476650e-04],
    [-7.34061576e-04,  1.58173584e-04,  7.94203179e-05, -1.31862863e-07, -3.37229272e-06,  9.14971953e-06, -3.76133213e-06,  1.77008996e-06, -1.21121124e-05, -3.73554489e-05],
    [-5.24567026e-04,  7.94203179e-05,  8.59323949e-05, 2.35199731e-06, -1.13519916e-05,  9.40107280e-06, -2.70260555e-07,  4.67273702e-06, -5.70480957e-07, -1.91226137e-05],
    [-5.58826254e-05, -1.31862863e-07,  2.35199731e-06, 6.00201516e-04, -1.90169960e-04, -1.50186049e-04, -4.85186524e-05,  8.06857181e-07,  3.77029033e-07, -1.11496332e-05],
    [-3.49010194e-05, -3.37229272e-06, -1.13519916e-05, -1.90169960e-04,  1.88005486e-04, -1.37342080e-05, -3.93314838e-07, -1.67706048e-06,  1.37292127e-05, -4.45906826e-06],
    [-2.57457388e-04,  9.14971953e-06,  9.40107280e-06, -1.50186049e-04, -1.37342080e-05,  6.60873010e-04, -4.01279290e-05,  9.59957151e-07,  3.71917102e-07, -2.24086598e-06],
    [ 3.07743337e-05, -3.76133213e-06, -2.70260555e-07, -4.85186524e-05, -3.93314838e-07, -4.01279290e-05, 1.81041818e-04,  9.83194837e-07, -2.27713928e-06, 2.88637902e-06],
    [-3.04906702e-05,  1.77008996e-06,  4.67273702e-06, 8.06857181e-07, -1.67706048e-06,  9.59957151e-07, 9.83194837e-07,  4.81661068e-05, -2.86184652e-05, -3.20842059e-06],
    [ 1.91838627e-05, -1.21121124e-05, -5.70480957e-07, 3.77029033e-07,  1.37292127e-05,  3.71917102e-07, -2.27713928e-06, -2.86184652e-05,  5.58173980e-05, 3.64437258e-07],
    [ 1.26476650e-04, -3.73554489e-05, -1.91226137e-05, -1.11496332e-05, -4.45906826e-06, -2.24086598e-06, 2.88637902e-06, -3.20842059e-06,  3.64437258e-07,7.97419499e-05]
  ]),
 'df_resid': 5672,
 'scale': 0.2117791586995399,
 'unweighted_rmse': 0.20774608617342513,
 'nobs': 5682,
 'rsquared': 0.4975048207157158,
 'weights_normalized': True}


MODELO_BASE['CHILE'] = {
  'coefs': {
     'const': -35.28135312449055,
    'CALEFACCION_electrico': -0.7849438634089401,
    'AIRE_ACONDICIONADO': 0.5332813348260148,
    'AGUA_CALIENTE_electrica': 0.02233944840823343,
    'VENTANAS_log': 0.8915352020395764,
    'DORMITORIOS_log': 1.1286927099564847,
    'HABITANTES_totales_log': 0.6943882161221977,
    'CLIMA_grados_dias_calefaccion_log': 23.370819228842834,
    'CLIMA_grados_dias_enfriamiento_log': -0.4461417276925326,
    'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': -0.20317563962628898,
    'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': 0.27759756806618174,
    'CLIMA_grados_dias_calefaccion_log_2': -3.6241690026815316,
    'CLIMA_grados_dias_enfriamiento_log_2': 0.2113218394637681,
    'VENTANAS_log_X_DORMITORIOS_log': -0.45814324890253655,
    'VENTANAS_log_X_CLIMA_grados_dias_enfriamiento_log': -0.24739716669808576,
    'DORMITORIOS_log_X_HABITANTES_totales_log': -0.8606681093577948},
 'cov': np.array([[ 
    7.54983153e+01, -2.65783376e-01,  2.54876430e-02, 3.72617327e-02,  5.38139449e-02,  1.34996386e-01,  1.83187022e-02, -4.72499465e+01,  1.03076165e+00, -1.01779366e-02,  8.25601401e-02,  7.29805417e+00, -2.97235892e-01, -1.06667440e-01, -5.82990548e-03, -6.36537453e-02],
       [-2.65783376e-01,  3.10945911e-01,  5.58944308e-03, -1.42425903e-03, -1.81420306e-03, -3.36329224e-03, -4.09331518e-04,  1.64729536e-01, -7.90354978e-04, -2.42834987e-03, -1.00015780e-01, -2.51446505e-02, 2.61247408e-04,  4.57692954e-03, -6.28835448e-04, -4.20246008e-04],
       [ 2.54876430e-02,  5.58944308e-03,  1.14073230e-02,  5.96458416e-05, -6.44384340e-04,  7.91172506e-04, 4.04871135e-04, -1.58033021e-02,  4.33594248e-05, -4.86320215e-03, -1.80176157e-03,  2.44419974e-03,  -5.15918355e-05,  2.02164313e-04,  2.41331107e-04, -1.49120235e-03],
       [ 3.72617327e-02, -1.42425903e-03,  5.96458416e-05, 3.62461650e-04,  9.91645107e-05, -1.40591967e-04, -4.26430181e-05, -2.32587708e-02,  5.41716530e-04, -4.13332304e-05,  4.49607904e-04,  3.57764831e-03, -1.35634438e-04,  1.41210080e-04, -7.68993259e-05, 8.42040521e-05],
       [ 5.38139449e-02, -1.81420306e-03, -6.44384340e-04, 9.91645107e-05,  2.57061567e-02,  2.42641591e-02, -2.85721789e-04, -4.67128894e-02,  6.85200200e-03, 3.59075534e-04,  5.56967959e-04,  7.06621627e-03, -4.04391929e-04, -2.79352795e-02, -6.30308791e-03, 2.05685481e-05],
       [ 1.34996386e-01, -3.36329224e-03,  7.91172506e-04, -1.40591967e-04,  2.42641591e-02,  7.79619461e-02, 1.71342984e-02, -1.04750242e-01,  2.69128204e-03, -3.32509720e-04,  1.02642775e-03,  1.61540230e-02, -8.54017989e-04, -5.67770597e-02, -2.62714964e-05, -4.08031593e-02],
       [ 1.83187022e-02, -4.09331518e-04,  4.04871135e-04, -4.26430181e-05, -2.85721789e-04,  1.71342984e-02, 1.30280413e-02, -1.67051808e-02,  5.82746368e-04, -2.25599650e-04,  1.32831867e-04,  2.61690809e-03, -1.37992549e-04,  8.19918083e-04, -9.88733032e-05, -2.83609413e-02],
       [-4.72499465e+01,  1.64729536e-01, -1.58033021e-02, -2.32587708e-02, -4.67128894e-02, -1.04750242e-01,  -1.67051808e-02,  2.95886048e+01, -6.51329887e-01, 6.28587303e-03, -5.11833817e-02, -4.57111055e+00, 1.86621137e-01,  8.14053326e-02,  6.93778586e-03, 5.11605655e-02], 
       [ 1.03076165e+00, -7.90354978e-04,  4.33594248e-05, 5.41716530e-04,  6.85200200e-03,  2.69128204e-03, 5.82746368e-04, -6.51329887e-01,  1.88487324e-02, 1.40988557e-05,  2.25464662e-04,  1.00841153e-01, -4.53060591e-03, -1.99349202e-03, -3.10780936e-03, -1.74483568e-03],
       [-1.01779366e-02, -2.42834987e-03, -4.86320215e-03, -4.13332304e-05,  3.59075534e-04, -3.32509720e-04, -2.25599650e-04,  6.28587303e-03,  1.40988557e-05, 2.19657983e-03,  7.79386837e-04, -9.72179190e-04, 1.51086527e-05, -2.34932476e-04, -1.21188723e-04, 7.99507238e-04],
       [ 8.25601401e-02, -1.00015780e-01, -1.80176157e-03, 4.49607904e-04,  5.56967959e-04,  1.02642775e-03, 1.32831867e-04, -5.11833817e-02,  2.25464662e-04, 7.79386837e-04,  3.21907434e-02,  7.81495355e-03, -7.27149002e-05, -1.39466297e-03,  1.94146925e-04, 1.25776152e-04],
       [ 7.29805417e+00, -2.51446505e-02,  2.44419974e-03, 3.57764831e-03,  7.06621627e-03,  1.61540230e-02, 2.61690809e-03, -4.57111055e+00,  1.00841153e-01, -9.72179190e-04,  7.81495355e-03,  7.06312713e-01, -2.88607641e-02, -1.25144057e-02, -1.03134257e-03, -7.92286741e-03],
       [-2.97235892e-01,  2.61247408e-04, -5.15918355e-05, -1.35634438e-04, -4.04391929e-04, -8.54017989e-04, -1.37992549e-04,  1.86621137e-01, -4.53060591e-03, 1.51086527e-05, -7.27149002e-05, -2.88607641e-02, 1.27618324e-03,  6.66146662e-04,  7.55706384e-05, 3.81905649e-04],
       [-1.06667440e-01,  4.57692954e-03,  2.02164313e-04, 1.41210080e-04, -2.79352795e-02, -5.67770597e-02, 8.19918083e-04,  8.14053326e-02, -1.99349202e-03, -2.34932476e-04, -1.39466297e-03, -1.25144057e-02, 6.66146662e-04,  6.45469708e-02, -8.92882778e-06, -1.83948505e-03],
       [-5.82990548e-03, -6.28835448e-04,  2.41331107e-04, -7.68993259e-05, -6.30308791e-03, -2.62714964e-05, -9.88733032e-05,  6.93778586e-03, -3.10780936e-03, -1.21188723e-04,  1.94146925e-04, -1.03134257e-03, 7.55706384e-05, -8.92882778e-06,  3.19553161e-03, 4.87239980e-04],
       [-6.36537453e-02, -4.20246008e-04, -1.49120235e-03, 8.42040521e-05,  2.05685481e-05, -4.08031593e-02, -2.83609413e-02,  5.11605655e-02, -1.74483568e-03, 7.99507238e-04,  1.25776152e-04, -7.92286741e-03, 3.81905649e-04, -1.83948505e-03,  4.87239980e-04, 6.71404214e-02]]), 
 'df_resid': 3484,
 'scale': 0.2540806350052061,
 'unweighted_rmse': 0.23775023324303746,
 'nobs': 3500,
 'rsquared': 0.14184671602644616,
 'weights_normalized': True}




#MODELO AVANZADO ---------
MODELO_AVANZADO = {}
# En desuso por ahora



#OTROS MODELOS ---------  
MODELOS_CATEGORIAS = {}
MODELOS_CATEGORIAS['USA'] = {'AGUA_SANITARIA': {'const': -0.09104648123676526, 'CLIMA_grados_dias_enfriamiento_log': -0.30483110533879176, 'CLIMA_grados_dias_calefaccion_log': 0.1850515313394157, 'DORMITORIOS_log': -0.40809906780141836, 'VENTANAS_log': -0.488954133266386, 'HABITANTES_mayores_log': 2.2576779488622365, 'HABITANTES_menores_log': 1.1914427372165903, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': -0.047167475166271504, 'CALEFACCION_electrico': 0.16001140501610586, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': 0.04142613673092032, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -0.1539499049314573, 'AGUA_CALIENTE_electrica': -0.09104648123676509, 'AGUA_CALIENTE_electrica_X_AGUA_CALIENTE_tamano_log': 0.044894758426246684, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.21152705582274275, 'REFRIGERADOR_log': -0.39838034263387223, 'FREEZER_log': -0.277956176287728, 'TV_log_X_TV_frecuencia_semana_log': -0.21645517846858184, 'LUCES_afuera_log': -0.417511573847914, 'LUCES_afuera_log_X_LUCES_4_horas_log': 0.12735974577162978, 'LUCES_4_horas_log': -0.39694502971297935, 'HORNO_electrico': 0.01766029349790411}, 
                             'AIRE_ACONDICIONADO': {'const': -10.742075712173142, 'CLIMA_grados_dias_enfriamiento_log': 1.3694878354599798, 'CLIMA_grados_dias_calefaccion_log': 0.24967954993037678, 'DORMITORIOS_log': 0.4304227029362976, 'VENTANAS_log': 0.7295451571556427, 'HABITANTES_mayores_log': -0.44456277963667684, 'HABITANTES_menores_log': -0.16542688184968707, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': 1.369487835459998, 'CALEFACCION_electrico': 1.3557963038203171, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': -0.09267358375192111, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -0.5674220921820344, 'AGUA_CALIENTE_electrica': -0.5555903973017412, 'AGUA_CALIENTE_electrica_X_AGUA_CALIENTE_tamano_log': 0.09233158048267322, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.21613518828858336, 'REFRIGERADOR_log': -0.49170799039443763, 'FREEZER_log': -0.02768481192765675, 'TV_log_X_TV_frecuencia_semana_log': -0.1439677445028234, 'LUCES_afuera_log': 0.2702153789206119, 'LUCES_afuera_log_X_LUCES_4_horas_log': -0.03896992581069472, 'LUCES_4_horas_log': -0.3466663636618456, 'HORNO_electrico': -0.04356397890929541}, 
                             'CALEFACCION': {'const': -3.8986290213152692, 'CLIMA_grados_dias_enfriamiento_log': 0.5944698619679328, 'CLIMA_grados_dias_calefaccion_log': 0.8420197776218068, 'DORMITORIOS_log': 0.18321860742410762, 'VENTANAS_log': -1.2031860835387724, 'HABITANTES_mayores_log': -0.7625309061026752, 'HABITANTES_menores_log': -0.45245724221459965, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': -0.09963537576419638, 'CALEFACCION_electrico': -3.8986290213152794, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': 0.505217126649678, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': 0.8420197776218242, 'AGUA_CALIENTE_electrica': -0.7886436324307238, 'AGUA_CALIENTE_electrica_X_AGUA_CALIENTE_tamano_log': 0.18735682736754203, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.019812826458512053, 'REFRIGERADOR_log': -0.4469423978035168, 'FREEZER_log': -0.02975841159971553, 'TV_log_X_TV_frecuencia_semana_log': -0.07173570440742555, 'LUCES_afuera_log': 0.305205728545294, 'LUCES_afuera_log_X_LUCES_4_horas_log': 0.04033434987696442, 'LUCES_4_horas_log': -0.46915985417339534, 'HORNO_electrico': 0.039962896662151824}, 
                             'COCINA': {'const': -2.9195121073716077, 'CLIMA_grados_dias_enfriamiento_log': -0.26382197671760343, 'CLIMA_grados_dias_calefaccion_log': 0.18283961518625083, 'DORMITORIOS_log': -0.3550870680584222, 'VENTANAS_log': 0.6756580507092685, 'HABITANTES_mayores_log': 0.3693482272117354, 'HABITANTES_menores_log': 0.05117024244073268, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': -0.0933590042692044, 'CALEFACCION_electrico': 0.6158866440444895, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': -0.1715458724125824, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -0.26032604411611354, 'AGUA_CALIENTE_electrica': -0.32736719808470355, 'AGUA_CALIENTE_electrica_X_AGUA_CALIENTE_tamano_log': 0.0055222309721307955, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.12937973667601166, 'REFRIGERADOR_log': -0.43141479822415313, 'FREEZER_log': -0.394120217431251, 'TV_log_X_TV_frecuencia_semana_log': -0.17148003289760702, 'LUCES_afuera_log': -0.29900899506640494, 'LUCES_afuera_log_X_LUCES_4_horas_log': 0.18270452387497949, 'LUCES_4_horas_log': 0.017405002608968326, 'HORNO_electrico': 0.8455991873623551}, 
                             'REFRIGERACION': {'const': -1.401229191020899, 'CLIMA_grados_dias_enfriamiento_log': -0.1495543802442839, 'CLIMA_grados_dias_calefaccion_log': 0.1797762915126264, 'DORMITORIOS_log': -0.2836160572592931, 'VENTANAS_log': 0.3438040623755854, 'HABITANTES_mayores_log': -0.5346297193631584, 'HABITANTES_menores_log': -0.32061296096352926, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': -0.1131077725109394, 'CALEFACCION_electrico': 0.8168663534225756, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': -0.17459654125118645, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -0.3388151385885839, 'AGUA_CALIENTE_electrica': -0.2189559117010656, 'AGUA_CALIENTE_electrica_X_AGUA_CALIENTE_tamano_log': -0.08082289809504059, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.2224582323325118, 'REFRIGERADOR_log': 2.0762515033607425, 'FREEZER_log': 1.1734622179886298, 'TV_log_X_TV_frecuencia_semana_log': -0.36334036917781526, 'LUCES_afuera_log': -0.017465907288916383, 'LUCES_afuera_log_X_LUCES_4_horas_log': -0.10629712652266028, 'LUCES_4_horas_log': -0.0552549597667621, 'HORNO_electrico': -0.08977110571538563}, 
                             'LAVADO': {'const': -2.044764356469954, 'CLIMA_grados_dias_enfriamiento_log': -0.20793234513402326, 'CLIMA_grados_dias_calefaccion_log': 0.12388432151973416, 'DORMITORIOS_log': -0.5299240779111782, 'VENTANAS_log': -0.1617265584346784, 'HABITANTES_mayores_log': -0.20458204556795123, 'HABITANTES_menores_log': -0.1425268247151145, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': -0.07491659229258646, 'CALEFACCION_electrico': 0.6748648519108218, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': -0.07321822373506526, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -0.29185714656227013, 'AGUA_CALIENTE_electrica': -0.22457972466022394, 'AGUA_CALIENTE_electrica_X_AGUA_CALIENTE_tamano_log': -0.0903587248152497, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': 2.56681092279808, 'REFRIGERADOR_log': -0.7394812843924963, 'FREEZER_log': -0.509919042734314, 'TV_log_X_TV_frecuencia_semana_log': -0.20988681772177256, 'LUCES_afuera_log': -0.1820055257384128, 'LUCES_afuera_log_X_LUCES_4_horas_log': -0.005059106372739439, 'LUCES_4_horas_log': -0.14221609882313313, 'HORNO_electrico': -0.030856132104957724}, 
                             'ILUMINACION': {'const': -2.3019695549958907, 'CLIMA_grados_dias_enfriamiento_log': -0.003811003872089158, 'CLIMA_grados_dias_calefaccion_log': 0.11030513371936354, 'DORMITORIOS_log': -0.5180237564188847, 'VENTANAS_log': -0.5484280150829177, 'HABITANTES_mayores_log': -0.6069880701477905, 'HABITANTES_menores_log': -0.19126964656339374, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': -0.0785091521629928, 'CALEFACCION_electrico': 1.0465304614878337, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': 0.055713183338070016, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -0.39748587151195985, 'AGUA_CALIENTE_electrica': -0.4050902072735114, 'AGUA_CALIENTE_electrica_X_AGUA_CALIENTE_tamano_log': 0.0015037253684474505, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.23292505905811312, 'REFRIGERADOR_log': -0.49423153746369713, 'FREEZER_log': -0.4981110807351972, 'TV_log_X_TV_frecuencia_semana_log': -0.22256500286729164, 'LUCES_afuera_log': 0.15833778732816456, 'LUCES_afuera_log_X_LUCES_4_horas_log': -0.23063754733995118, 'LUCES_4_horas_log': 2.1609632499619877, 'HORNO_electrico': -0.007239594960330872}, 
                             'TV': {'const': -1.7890132044231288, 'CLIMA_grados_dias_enfriamiento_log': -0.2506399280010186, 'CLIMA_grados_dias_calefaccion_log': 0.18924139573838003, 'DORMITORIOS_log': -0.43296370869271883, 'VENTANAS_log': 0.21475282215717056, 'HABITANTES_mayores_log': -0.20893400766829073, 'HABITANTES_menores_log': -0.13584276022213687, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': -0.0795358020883245, 'CALEFACCION_electrico': 0.760160347527241, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': -0.14428124766488779, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -0.3196506824773231, 'AGUA_CALIENTE_electrica': -0.22213507354394924, 'AGUA_CALIENTE_electrica_X_AGUA_CALIENTE_tamano_log': -0.08088578100211695, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.2796769249588805, 'REFRIGERADOR_log': -0.41291248773383477, 'FREEZER_log': -0.4233997220766172, 'TV_log_X_TV_frecuencia_semana_log': 1.5801153121564702, 'LUCES_afuera_log': -0.45834879049309446, 'LUCES_afuera_log_X_LUCES_4_horas_log': 0.10233584481292603, 'LUCES_4_horas_log': -0.21049559889937777, 'HORNO_electrico': -0.05557889627106596}, 
                             'OTROS': {'const': 0.7137435548324682, 'CLIMA_grados_dias_enfriamiento_log': -0.2529354889015297, 'CLIMA_grados_dias_calefaccion_log': -0.1680778952504179, 'DORMITORIOS_log': 0.41091579814931095, 'VENTANAS_log': -0.8718440159460923, 'HABITANTES_mayores_log': 0.18162172547382677, 'HABITANTES_menores_log': -0.04673722619921015, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': -0.08816823386443359, 'CALEFACCION_electrico': 1.3455101086549217, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': 0.2598776747563732, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -0.5594380586687437, 'AGUA_CALIENTE_electrica': -0.5161855014209948, 'AGUA_CALIENTE_electrica_X_AGUA_CALIENTE_tamano_log': -0.035725814106555606, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.2053810913401378, 'REFRIGERADOR_log': 0.18349149306382098, 'FREEZER_log': -0.006661715575337725, 'TV_log_X_TV_frecuencia_semana_log': -0.12275989365718795, 'LUCES_afuera_log': 0.08651071322964732, 'LUCES_afuera_log_X_LUCES_4_horas_log': 0.10671916822007789, 'LUCES_4_horas_log': -0.36990800664990475, 'HORNO_electrico': -0.028706449062528488}}

MODELOS_CATEGORIAS['CHILE'] = {
   'AGUA_SANITARIA': {'const': 2.9265545228362866, 'VENTANAS_log': 25.32878395002117, 'HABITANTES_totales_log': 2.7765199598053414, 'DORMITORIOS_log': 0.24441729510606613, 'AGUA_CALIENTE_electrica': 2.926554522836404, 'CALEFACCION_electrico': 4.823627876105736, 'SECARROPAS_electrico': -0.15807778228575625, 'AIRE_ACONDICIONADO': -1.1863521090585194, 'HORNO_electrico': -0.24090064763763863, 'CLIMA_grados_dias_enfriamiento_log': 1.5660092582482612, 'CLIMA_grados_dias_calefaccion_log': -11.215849987040754, 'LUCES_4_horas_log': 0.36784748303059056, 'LUCES_afuera_log': -0.019964215775811395, 'REFRIGERADOR_log': 0.954348041518474, 'FREEZER_log': -0.3911003128865846, 'LAVARROPAS_frecuencia_log': -0.07858905215778389, 'TV_log': -1.4946267673478855, 'TV_frecuencia_log': 0.9587714711214312, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': 0.47213131428984323, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': -7.332199394807469, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -1.6321710925678665, 'TV_log_X_TV_frecuencia_semana_log': 0.32355586549418824, 'LUCES_afuera_log_X_LUCES_4_horas_log': 0.2415265376787652, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.2671333167033319, 'VENTANAS_log_X_CLIMA_grados_dias_enfriamiento_log': -1.1614273212196762, 'VENTANAS_log_X_DORMITORIOS_log': -0.17457216383803686, 'DORMITORIOS_log_X_HABITANTES_totales_log': -0.4177336048137722, 'CLIMA_grados_dias_calefaccion_log_2': 2.645498475193226, 'CLIMA_grados_dias_enfriamiento_log_2': -0.24811094922866014, 'TV_frecuencia_log_2': -0.6099207780016743, 'LUCES_4_horas_log_2': -0.8064021594442}, 
   'AIRE_ACONDICIONADO': {'const': -217.97722462018066, 'VENTANAS_log': 67.98623664108821, 'HABITANTES_totales_log': 0.677369393773062, 'DORMITORIOS_log': 12.108825493330508, 'AGUA_CALIENTE_electrica': -0.9376387424207048, 'CALEFACCION_electrico': 9.981820330765133, 'SECARROPAS_electrico': -0.18145384152382477, 'AIRE_ACONDICIONADO': -217.97722462014607, 'HORNO_electrico': 0.23933824758279587, 'CLIMA_grados_dias_enfriamiento_log': 1.6390812974587063, 'CLIMA_grados_dias_calefaccion_log': 250.50631144863414, 'LUCES_4_horas_log': -0.31581706968220524, 'LUCES_afuera_log': -1.02134096507643, 'REFRIGERADOR_log': 3.728781186533141, 'FREEZER_log': 2.003958963746955, 'LAVARROPAS_frecuencia_log': 2.640323862370902, 'TV_log': -1.6031030721647788, 'TV_frecuencia_log': -4.906735751589279, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': 1.639081297454445, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': -19.377910739177338, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -2.9403180728760203, 'TV_log_X_TV_frecuencia_semana_log': 2.9991553381416267, 'LUCES_afuera_log_X_LUCES_4_horas_log': 0.04080731785663843, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.7976861551508966, 'VENTANAS_log_X_CLIMA_grados_dias_enfriamiento_log': -2.4472131856896366, 'VENTANAS_log_X_DORMITORIOS_log': -8.637563979498953, 'DORMITORIOS_log_X_HABITANTES_totales_log': -5.610948961257086, 'CLIMA_grados_dias_calefaccion_log_2': -36.57874491981265, 'CLIMA_grados_dias_enfriamiento_log_2': -0.09536475502781559, 'TV_frecuencia_log_2': 1.5091611634959874, 'LUCES_4_horas_log_2': 0.4173133759695823}, 
  'CALEFACCION': {'const': -173.58267010862457, 'VENTANAS_log': -22.895665202360718, 'HABITANTES_totales_log': -1.6488472807163874, 'DORMITORIOS_log': -3.3392796526997097, 'AGUA_CALIENTE_electrica': -0.3303211819330662, 'CALEFACCION_electrico': -173.58267010855906, 'SECARROPAS_electrico': 0.07841862348499655, 'AIRE_ACONDICIONADO': -0.010515858269097587, 'HORNO_electrico': -0.18889002286497028, 'CLIMA_grados_dias_enfriamiento_log': -3.792074180482433, 'CLIMA_grados_dias_calefaccion_log': 107.27541980366716, 'LUCES_4_horas_log': -0.6065355410023311, 'LUCES_afuera_log': -0.06249411452842916, 'REFRIGERADOR_log': -0.45129082399663906, 'FREEZER_log': -0.4405882366213997, 'LAVARROPAS_frecuencia_log': 0.52532887247978, 'TV_log': -0.060443243438557934, 'TV_frecuencia_log': 1.0792624313631678, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': -0.19861078278905617, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': 6.368537470325746, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': 107.27541980366205, 'TV_log_X_TV_frecuencia_semana_log': -0.09645567854310604, 'LUCES_afuera_log_X_LUCES_4_horas_log': -0.7351847879643982, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.672951095634307, 'VENTANAS_log_X_CLIMA_grados_dias_enfriamiento_log': 1.4072186324781637, 'VENTANAS_log_X_DORMITORIOS_log': 1.0047640953411947, 'DORMITORIOS_log_X_HABITANTES_totales_log': 3.7099296904319377, 'CLIMA_grados_dias_calefaccion_log_2': -32.80936172233848, 'CLIMA_grados_dias_enfriamiento_log_2': 1.0866511573269966, 'TV_frecuencia_log_2': -0.5823017777720016, 'LUCES_4_horas_log_2': 1.3447165403976604}, 
  'COCINA': {'const': -39.405353391480375, 'VENTANAS_log': 28.35091732233362, 'HABITANTES_totales_log': 4.799751335600377, 'DORMITORIOS_log': 9.89527065147078, 'AGUA_CALIENTE_electrica': -3.7193126498738573, 'CALEFACCION_electrico': 13.00653087752068, 'SECARROPAS_electrico': -0.1657875376182006, 'AIRE_ACONDICIONADO': -15.161401892352169, 'HORNO_electrico': -39.4053533914805, 'CLIMA_grados_dias_enfriamiento_log': 4.239271495231447, 'CLIMA_grados_dias_calefaccion_log': 28.26763890550283, 'LUCES_4_horas_log': -1.5857160813129165, 'LUCES_afuera_log': -0.8092533032793237, 'REFRIGERADOR_log': 2.8319478200536623, 'FREEZER_log': 0.40063494010870615, 'LAVARROPAS_frecuencia_log': -1.0423534722246977, 'TV_log': 1.5521500545676352, 'TV_frecuencia_log': 3.6598711619763815, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': 6.58109736278596, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': -7.449855408458912, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -4.328406566254321, 'TV_log_X_TV_frecuencia_semana_log': -2.6995865518589217, 'LUCES_afuera_log_X_LUCES_4_horas_log': 3.1728336924546463, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.34747574336279125, 'VENTANAS_log_X_CLIMA_grados_dias_enfriamiento_log': -3.038884556514059, 'VENTANAS_log_X_DORMITORIOS_log': -1.3700766849057078, 'DORMITORIOS_log_X_HABITANTES_totales_log': -10.635923623325192, 'CLIMA_grados_dias_calefaccion_log_2': -2.7423490378203232, 'CLIMA_grados_dias_enfriamiento_log_2': -0.23947009132908176, 'TV_frecuencia_log_2': -0.9794199691237775, 'LUCES_4_horas_log_2': 1.87973430872469}, 
  'REFRIGERACION': {'const': 11.65220967434913, 'VENTANAS_log': 1.7725371785880726, 'HABITANTES_totales_log': -0.6872154266174185, 'DORMITORIOS_log': -0.7038940767707174, 'AGUA_CALIENTE_electrica': -0.9337998386509954, 'CALEFACCION_electrico': 5.610293219766341, 'SECARROPAS_electrico': -0.4809597084406917, 'AIRE_ACONDICIONADO': -0.21991363916134504, 'HORNO_electrico': -0.2162981898076089, 'CLIMA_grados_dias_enfriamiento_log': 0.5869564640107959, 'CLIMA_grados_dias_calefaccion_log': -8.315930709250516, 'LUCES_4_horas_log': -0.23045704977648943, 'LUCES_afuera_log': -0.38348517683217764, 'REFRIGERADOR_log': 0.9821417778250472, 'FREEZER_log': 0.44129517777649285, 'LAVARROPAS_frecuencia_log': -0.4139032088834568, 'TV_log': -0.6724248934150455, 'TV_frecuencia_log': 0.25913792127748575, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': 0.10797875539404721, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': -0.5623313417188938, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -1.9172331626191974, 'TV_log_X_TV_frecuencia_semana_log': -0.11040148502109014, 'LUCES_afuera_log_X_LUCES_4_horas_log': 0.38266253101485637, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': 0.14278827877207473, 'VENTANAS_log_X_CLIMA_grados_dias_enfriamiento_log': 0.007112973421116414, 'VENTANAS_log_X_DORMITORIOS_log': 0.11733153460786427, 'DORMITORIOS_log_X_HABITANTES_totales_log': 0.8373722391208644, 'CLIMA_grados_dias_calefaccion_log_2': 1.4151832004535572, 'CLIMA_grados_dias_enfriamiento_log_2': -0.1639915319335448, 'TV_frecuencia_log_2': -0.23357126451051774, 'LUCES_4_horas_log_2': -0.4101731408417621}, 
  'LAVADO': {'const': 51.57162927728834, 'VENTANAS_log': 1.1745104935405783, 'HABITANTES_totales_log': 0.20646212206919246, 'DORMITORIOS_log': -0.30270995270787354, 'AGUA_CALIENTE_electrica': -0.556111829353838, 'CALEFACCION_electrico': 1.6080285311610167, 'SECARROPAS_electrico': 51.57162927728997, 'AIRE_ACONDICIONADO': -0.31112343119583913, 'HORNO_electrico': 0.014289850220325946, 'CLIMA_grados_dias_enfriamiento_log': 1.1086333762685237, 'CLIMA_grados_dias_calefaccion_log': -65.45050920478309, 'LUCES_4_horas_log': 0.3319995056431671, 'LUCES_afuera_log': -0.13953107334666387, 'REFRIGERADOR_log': -0.36343769140224397, 'FREEZER_log': -0.0042028327435565, 'LAVARROPAS_frecuencia_log': 0.3583905406780319, 'TV_log': -0.796995308947621, 'TV_frecuencia_log': 0.12384093734816388, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': 0.12002345499073118, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': -0.4735078610203858, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -0.5694185217980859, 'TV_log_X_TV_frecuencia_semana_log': 0.23174888868108068, 'LUCES_afuera_log_X_LUCES_4_horas_log': -0.3783479141403951, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': 0.3583905406774963, 'VENTANAS_log_X_CLIMA_grados_dias_enfriamiento_log': -0.08669922787921298, 'VENTANAS_log_X_DORMITORIOS_log': 0.2783852192877957, 'DORMITORIOS_log_X_HABITANTES_totales_log': -0.1802527200287552, 'CLIMA_grados_dias_calefaccion_log_2': 10.181024680867344, 'CLIMA_grados_dias_enfriamiento_log_2': -0.2846128243114037, 'TV_frecuencia_log_2': -0.20744671480486176, 'LUCES_4_horas_log_2': -0.5449088835664286}, 
  'ILUMINACION': {'const': 147.616036542663, 'VENTANAS_log': -13.134022074180967, 'HABITANTES_totales_log': 0.043405033485021435, 'DORMITORIOS_log': -1.848749969986619, 'AGUA_CALIENTE_electrica': -0.8036756053175058, 'CALEFACCION_electrico': 1.527229821575225, 'SECARROPAS_electrico': -0.2131389685790414, 'AIRE_ACONDICIONADO': 0.023328700038826894, 'HORNO_electrico': -0.16899025755612235, 'CLIMA_grados_dias_enfriamiento_log': 0.842597392475013, 'CLIMA_grados_dias_calefaccion_log': -87.99492004145512, 'LUCES_4_horas_log': 1.0887919432069053, 'LUCES_afuera_log': 0.6754260214089856, 'REFRIGERADOR_log': -0.5050281889943986, 'FREEZER_log': -0.26044049489409304, 'LAVARROPAS_frecuencia_log': 0.10112444110586433, 'TV_log': -0.9612633325374211, 'TV_frecuencia_log': 0.3981538976821892, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': -0.12185843210376776, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': 3.2815985456063794, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -0.5938339599126556, 'TV_log_X_TV_frecuencia_semana_log': 0.29369909556818335, 'LUCES_afuera_log_X_LUCES_4_horas_log': -0.38311561422961155, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.04184839875674437, 'VENTANAS_log_X_CLIMA_grados_dias_enfriamiento_log': 0.8080285060706178, 'VENTANAS_log_X_DORMITORIOS_log': 2.645109658115307, 'DORMITORIOS_log_X_HABITANTES_totales_log': -0.95938028733323, 'CLIMA_grados_dias_calefaccion_log_2': 13.043606345024903, 'CLIMA_grados_dias_enfriamiento_log_2': -0.4596772360053689, 'TV_frecuencia_log_2': -0.37529656512612225, 'LUCES_4_horas_log_2': -0.10536942893563175}, 
  'TV': {'const': -164.4589036991883, 'VENTANAS_log': 1.2986796496499369, 'HABITANTES_totales_log': -0.6276518779770606, 'DORMITORIOS_log': 0.8793621430108509, 'AGUA_CALIENTE_electrica': -0.9093312365677411, 'CALEFACCION_electrico': 2.4828177240883114, 'SECARROPAS_electrico': -0.349986373635736, 'AIRE_ACONDICIONADO': -0.2897501210812702, 'HORNO_electrico': -0.24341448748104907, 'CLIMA_grados_dias_enfriamiento_log': -2.4096902427068563, 'CLIMA_grados_dias_calefaccion_log': 98.13936233784467, 'LUCES_4_horas_log': 0.04035743243493472, 'LUCES_afuera_log': -0.23090702907178337, 'REFRIGERADOR_log': -0.011831877316594897, 'FREEZER_log': -0.32555087146668027, 'LAVARROPAS_frecuencia_log': -0.36235259794104896, 'TV_log': 3.719690546047505, 'TV_frecuencia_log': 4.500480426914624, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': -0.02349498357831473, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': -0.4480485549714874, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -0.9149308610594019, 'TV_log_X_TV_frecuencia_semana_log': -1.5973561567315597, 'LUCES_afuera_log_X_LUCES_4_horas_log': 0.254241239359237, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': 0.04884243755289983, 'VENTANAS_log_X_CLIMA_grados_dias_enfriamiento_log': 0.3491908798031201, 'VENTANAS_log_X_DORMITORIOS_log': -1.3555935280528373, 'DORMITORIOS_log_X_HABITANTES_totales_log': 0.6663074918182988, 'CLIMA_grados_dias_calefaccion_log_2': -15.062206428765142, 'CLIMA_grados_dias_enfriamiento_log_2': 0.5938101934890432, 'TV_frecuencia_log_2': -0.5246325938442737, 'LUCES_4_horas_log_2': -0.43476490937090095}, 
  'OTROS': {'const': 57.96487811265677, 'VENTANAS_log': 4.761236421024372, 'HABITANTES_totales_log': 0.5643340538996033, 'DORMITORIOS_log': 1.5505865258726068, 'AGUA_CALIENTE_electrica': -1.1783562716249447, 'CALEFACCION_electrico': 3.6835580687344343, 'SECARROPAS_electrico': -0.04145640605800605, 'AIRE_ACONDICIONADO': 0.09386941194662676, 'HORNO_electrico': 0.25151045570790437, 'CLIMA_grados_dias_enfriamiento_log': 1.2472971950035314, 'CLIMA_grados_dias_calefaccion_log': -38.11612986544502, 'LUCES_4_horas_log': -0.3278391800041514, 'LUCES_afuera_log': 0.026791888852034557, 'REFRIGERADOR_log': 0.13486998455452862, 'FREEZER_log': 0.11534242373132271, 'LAVARROPAS_frecuencia_log': 0.2596505415761314, 'TV_log': 1.0541695499226895, 'TV_frecuencia_log': -0.0275367909543463, 'AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log': -0.07888429245842492, 'VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log': -0.9978655612961915, 'CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log': -1.2752339391995506, 'TV_log_X_TV_frecuencia_semana_log': -0.3475431306440472, 'LUCES_afuera_log_X_LUCES_4_horas_log': 0.05174857104659256, 'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log': -0.19272108482556985, 'VENTANAS_log_X_CLIMA_grados_dias_enfriamiento_log': -0.45929961495523547, 'VENTANAS_log_X_DORMITORIOS_log': -1.4628619660354878, 'DORMITORIOS_log_X_HABITANTES_totales_log': -0.4041560823899446, 'CLIMA_grados_dias_calefaccion_log_2': 5.917129600314108, 'CLIMA_grados_dias_enfriamiento_log_2': -0.2853162680688168, 'TV_frecuencia_log_2': -0.10500997603391171, 'LUCES_4_horas_log_2': 0.18452337598598045}}


#CUTPOINTS ---------
CUTPOINTS = {}
CUTPOINTS['USA'] = { 
    "Muy bajo":  (-np.inf, 4883.012),
    "Bajo":       (4883.012, 7722.177),
    "Promedio":       (7722.177, 10945.711),
    "Alto":      (10945.711, 15788.587),
    "Muy alto": (15788.587,  np.inf)
}

CUTPOINTS['CHILE'] = { 
    "Muy bajo":  (-np.inf, 1018.3),
    "Bajo":       (1018.3, 1465.5),
    "Promedio":       (1465.5, 1918.1),
    "Alto":      (1918.1, 2706.9),
    "Muy alto": (2706.9,  np.inf)
}





#PERCENTILES ---------
PERCENTILES = {}
PERCENTILES['USA'] = {
    0.05: 2483.479,
    0.10: 3389.987,
    0.15: 4150.0,
    0.20: 4883.012,
    0.25: 5609.369,
    0.30: 6323.614,
    0.35: 6997.806,
    0.40: 7722.177,
    0.45: 8464.097,
    0.50: 9300.434,
    0.55: 10020.797,
    0.60: 10945.711,
    0.65: 11947.0,
    0.70: 12986.41,
    0.75: 14316.106,
    0.80: 15788.587,
    0.85: 17518.615,
    0.90: 19974.706,
    0.95: 23642.508
}



PERCENTILES['CHILE'] = {0.05: np.float64(630.1410840046804),
 0.1: np.float64(785.5160075847832),
 0.15: np.float64(895.3539188570929),
 0.2: np.float64(1018.3101050228319),
 0.25: np.float64(1140.5574892690145),
 0.3: np.float64(1270.3197308866354),
 0.35: np.float64(1369.3663954832753),
 0.4: np.float64(1465.5433158250412),
 0.45: np.float64(1592.884613209357),
 0.5: np.float64(1695.225428814099),
 0.55: np.float64(1803.8599306679796),
 0.6: np.float64(1918.1384039970183),
 0.65: np.float64(2067.653022452022),
 0.7: np.float64(2248.2859344401163),
 0.75: np.float64(2450.123356327372),
 0.8: np.float64(2706.9009915289016),
 0.85: np.float64(3086.812246463281),
 0.9: np.float64(3598.605497096215),
 0.95: np.float64(4800.1685439974135)}

# Valida el cuestionario:


def predecir(obs: dict) -> dict:
    """Calcula el diagnostico energetico completo para una vivienda.

    obs: diccionario con las mismas claves que usaba INPUT.json
    (ver adaptador.payload_a_obs para construirlo desde el payload del wizard).
    Devuelve el mismo diccionario "result" que antes se escribia en OUTPUT.json.
    """
    advertencias = []
    cantidad_imputaciones_basico = 0
    cantidad_imputaciones_avanzado = 0
    reporte=[]

    if pd.isna(obs['dormitorios'] ):
      advertencias.append('Ha ocurrido un error grave en la codificación de la variable dormitorios; se lo reemplaza por la mediana')
      obs['dormitorios'] = 2  # Reemplaza por la mediana
      cantidad_imputaciones_basico +=1
    elif obs['dormitorios']<0:
      advertencias.append(f'dormitorios debe ser >=0 pero se introdujo: {obs['dormitorios']}; se lo reemplaza por la mediana')
      obs['dormitorios'] = 2  # Reemplaza por la mediana
      cantidad_imputaciones_basico +=1
    elif obs['dormitorios']==999:
      advertencias.append(f'Cantidad de dormitorios no disponible se reemplaza por la mediana')
      obs['dormitorios'] = 2  # Reemplaza por la mediana
      cantidad_imputaciones_basico +=1
    elif obs['dormitorios']>10:
      advertencias.append(f'Cantidad de dormitorios inusualmente alta se introdujo: {obs['dormitorios']}')



    '''
    IGNORAR:
    ['horno_electrico', 'agua_caliente_tamano', 'lavarropas_frecuencia', 'tv_cantidad', 'tv_frecuencia','freezer','refrigerador','luces_exterior', 'luces_interior_4_horas']:

    vars['DORMITORIOS_log'] =  np.log10( 1 + obs['dormitorios'] )
    vars['VENTANAS_log'] = np.log10( 1 + obs['ventanas'] )
    vars['HABITANTES_mayores_log'] =  np.log10( 1 + obs['habitantes_mayores'] )
    vars['HABITANTES_menores_log'] =  np.log10( 1 + obs['habitantes_menores'] )
    vars['HABITANTES_totales_log'] =  np.log10( 1 + obs['habitantes_menores'] + obs['habitantes_mayores'] )
    vars['AGUA_CALIENTE_electrica'] =  obs['agua_caliente_electrica']
    vars['CALEFACCION_electrico'] =  obs['calefaccion_electrica']
    vars['SECARROPAS_electrico'] =  obs['secarropas_electrico']
    vars['AIRE_ACONDICIONADO'] =  obs['aire_acondicionado']
    '''










    #Si tenemos datos del pais y provincia/estado los usamos, sino usamos los datos del pais.
    pais = PAISES[obs['pais']]
    if pais in ['USA', 'CHILE']:
      hdd = HDD[pais][obs['estado']]
      cdd = CDD[pais][obs['estado']]
    else:
      hdd = HDD[pais]
      cdd = CDD[pais]

    # Si el pais es distinto de USA o CHILE, se marca que es un modelo prestado.
    flag_modelo_prestado = False
    if pais in ['USA', 'CHILE']:
      pass
    elif pais in ['CANADA']:
      pais = 'USA'
      flag_modelo_prestado = True
    else:
      pais = 'CHILE'
      flag_modelo_prestado = True


    vars = {}
    vars['const'] = 1
    vars['DORMITORIOS_log'] =  np.log10( 1 + obs['dormitorios'] )
    vars['VENTANAS_log'] = np.log10( 1 + obs['ventanas'] )
    vars['HABITANTES_mayores_log'] =  np.log10( 1 + obs['habitantes_mayores'] )
    vars['HABITANTES_menores_log'] =  np.log10( 1 + obs['habitantes_menores'] )
    vars['HABITANTES_totales_log'] =  np.log10( 1 + obs['habitantes_menores'] + obs['habitantes_mayores'] )
    vars['AGUA_CALIENTE_electrica'] =  obs['agua_caliente_electrica']
    vars['CALEFACCION_electrico'] =  obs['calefaccion_electrica']
    vars['SECARROPAS_electrico'] =  obs['secarropas_electrico']
    vars['AIRE_ACONDICIONADO'] =  obs['aire_acondicionado']
    vars['CLIMA_grados_dias_enfriamiento_log'] =  np.log10( 1 + cdd )
    vars['CLIMA_grados_dias_calefaccion_log'] =  np.log10( 1 + hdd )

    vars['AIRE_ACONDICIONADO_X_CLIMA_grados_dias_enfriamiento_log'] =  vars['AIRE_ACONDICIONADO'] * vars['CLIMA_grados_dias_enfriamiento_log']
    vars['VENTANAS_log_X_CLIMA_grados_dias_calefaccion_log'] =  vars['VENTANAS_log'] * vars['CLIMA_grados_dias_calefaccion_log']    
    vars['VENTANAS_log_X_CLIMA_grados_dias_enfriamiento_log'] =  vars['VENTANAS_log'] * vars['CLIMA_grados_dias_enfriamiento_log']    
    vars['CALEFACCION_electrico_X_CLIMA_grados_dias_calefaccion_log'] =  vars['CALEFACCION_electrico'] * vars['CLIMA_grados_dias_calefaccion_log']

    vars['VENTANAS_log_X_DORMITORIOS_log'] =  vars['VENTANAS_log'] * vars['DORMITORIOS_log']
    vars['DORMITORIOS_log_X_HABITANTES_totales_log'] =  vars['DORMITORIOS_log'] * vars['HABITANTES_totales_log']


    vars['HORNO_electrico'] =  obs['horno_electrico']
    vars['AGUA_CALIENTE_tamano'] =  obs['agua_caliente_tamano']
    if obs['flag_galones'] ==2:
      vars['AGUA_CALIENTE_tamano'] =  obs['agua_caliente_tamano'] * 3.78541 #litros
    elif obs['flag_galones'] ==3:
      vars['AGUA_CALIENTE_tamano'] =  obs['agua_caliente_tamano']  * 1.20094   #galones imperiales 
    vars['AGUA_CALIENTE_tamano_log'] =  np.log10( 1 + vars['AGUA_CALIENTE_tamano'] )
    vars['AGUA_CALIENTE_electrica_X_AGUA_CALIENTE_tamano_log'] =  vars['AGUA_CALIENTE_electrica'] * vars['AGUA_CALIENTE_tamano_log']    

    vars['LAVARROPAS_frecuencia_log'] =  np.log10( 1 + obs['lavarropas_frecuencia'] )
    vars['SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log'] =  vars['LAVARROPAS_frecuencia_log'] * vars['SECARROPAS_electrico'] 
    vars['TV_log'] =  np.log10( 1 + obs['tv_cantidad'] )
    vars['TV_frecuencia_semana_log'] =  np.log10( 1 + obs['tv_frecuencia'] )
    # Alias: los coeficientes de MODELOS_CATEGORIAS['CHILE'] usan el nombre
    # 'TV_frecuencia_log' (sin '_semana') para este mismo valor; USA usa el
    # nombre completo. Se deja el alias para que ambos paises encuentren su clave.
    vars['TV_frecuencia_log'] = vars['TV_frecuencia_semana_log']
    vars['TV_log_X_TV_frecuencia_semana_log'] =  vars['TV_log'] * vars['TV_frecuencia_semana_log']
    vars['FREEZER_log'] =  np.log10( 1 + obs['freezer'] )
    vars['REFRIGERADOR_log'] =  np.log10( 1 + obs['refrigerador'] )

    vars['LUCES_afuera_log'] =  np.log10( 1 + obs['luces_exterior'] )
    vars['LUCES_4_horas_log'] =  np.log10( 1 + obs['luces_interior_4_horas'] )
    vars['LUCES_afuera_log_X_LUCES_4_horas_log'] =  vars['LUCES_afuera_log'] * vars['LUCES_4_horas_log']


    vars['CLIMA_grados_dias_calefaccion_log_2'] =  vars['CLIMA_grados_dias_calefaccion_log'] ** 2
    vars['CLIMA_grados_dias_enfriamiento_log_2'] =  vars['CLIMA_grados_dias_enfriamiento_log'] ** 2
    vars['TV_frecuencia_log_2'] = vars['TV_frecuencia_semana_log'] ** 2
    vars['LUCES_4_horas_log_2'] = vars['LUCES_4_horas_log'] ** 2

    if obs['periodo_anual']==0:
      vars['kwh'] = 12 * obs['kwh']
    elif obs['periodo_anual']==1:
      vars['kwh'] = obs['kwh']

    vars['logKWH'] = np.log10( 1 + vars['kwh'] )

    CONSUMO = vars['kwh']
    logKWH_real = vars['logKWH']

    #--------------------------
    #--- RANKING -----
    #---------------------------
    RANKING = 0
    pct_dict = PERCENTILES[pais]
    # Linear interpolation to find the percentile
    percentiles = np.array(list(pct_dict.keys()))
    values      = np.array(list(pct_dict.values()))

    # np.interp expects the x-coordinates to be increasing
    percentile = np.interp(CONSUMO, values, percentiles)

    # Handle values outside the range
    if CONSUMO <= values.min():
        percentile = 0.05          # or 0.0 if you prefer
    elif CONSUMO >= values.max():
        percentile = 0.95          # or 1.0 if you prefer
    RANKING = int(percentile * 100)   # Convert to percentage
    RANKING_INTERPRETACION = f"El hogar consume más electricidad que el {RANKING}% de las viviendas."
    # RESULTADOS -----
    # MODELO BASE
    logKWH_base = 0



    modelo = MODELO_BASE[ pais ]['coefs']
    cov =  MODELO_BASE[ pais ]['cov']
    for var, coef in modelo.items():
      logKWH_base +=  coef * vars[var] 


    # -------------------------------------------------
    # ----- PERFIL DE CONSUMO                       ---
    # -------------------------------------------------
    logkwh_base = 3.25          # predicted value for this house
    # your cutpoints
    cutpoints = CUTPOINTS[pais]

    PERFIL_DE_CONSUMO = None
    for cat, (lo, hi) in cutpoints.items():
        if lo <= 10**logkwh_base < hi:
            PERFIL_DE_CONSUMO = cat
            break



    # design vector for this house (must match the order of coefficients)
    x_row = {}
    for var in modelo.keys():
        if var == "const":
            x_row[var] = 1.0
        else:
            x_row[var] = vars.get(var, 0.0)


    # 2. Standard error of the prediction
    # -------------------------------------------------
    coef_names = list(modelo.keys())
    x = np.array([x_row[name] for name in coef_names])

    se = np.sqrt(x @ cov @ x)


    # -------------------------------------------------
    # 4. Probability that the true mean is in the assigned category
    # -------------------------------------------------

    lo = cutpoints[PERFIL_DE_CONSUMO][0]
    hi = cutpoints[PERFIL_DE_CONSUMO][1]
    CONFIANZA = stats.norm.cdf(hi, loc=logkwh_base, scale=se) - stats.norm.cdf(lo, loc=logkwh_base, scale=se)





    # CATEGORIAS DE CONSUMO
    # Predicción para las ceategorías de consumo ceradas, ejemplo: aire_acondicionado == 0 --> el porcentaje de consumo de aire acondicionado es 0% 
    filters = {
        "AGUA_SANITARIA": vars["AGUA_CALIENTE_electrica"] > 0,
        "AIRE_ACONDICIONADO": vars["AIRE_ACONDICIONADO"] > 0,
        "CALEFACCION": vars["CALEFACCION_electrico"] > 0,
        "COCINA": vars["HORNO_electrico"] > 0,
        "REFRIGERACION": (vars["REFRIGERADOR_log"] > 0) | (vars["FREEZER_log"] > 0),
        "LAVADO": vars["SECARROPAS_electrico"] > 0,
        "ILUMINACION": (vars['LUCES_afuera_log'] > 0) | (vars['LUCES_4_horas_log'] > 0),
        "TV": (vars['TV_log'] > 0) & (vars['TV_frecuencia_semana_log'] > 0),
        "OTROS": True,
    }

    pred_categoria = {}

    for model, use_model in filters.items():
        pred_categoria[model] = 0

        if use_model:
            for var, coef in MODELOS_CATEGORIAS[pais][(model)].items():
                pred_categoria[model] += coef * vars[var]
            #transforma logit  ---> porcentaje
            pred_categoria[model] = 1 / (1 + np.exp(-pred_categoria[model]))  # Sigmoid function to convert logit to probability

    # NORMALIZACION DE LOS PORCENTAJES
    total = sum(pred_categoria.values())
    if total > 0:
        pred_categoria = {k: v / total for k, v in pred_categoria.items()}
    else:
        # Fallback if every prediction is zero
        pred_categoria = {k: 0 for k in pred_categoria}

    pred_per = {
        k: round(v * 100)
        for k, v in pred_categoria.items()
    }




    # -------------------------------------------------
    # 2. INDICE_DE_EFICIENCIA  (-100 to +100)
    # -------------------------------------------------
    residual = logKWH_real - logKWH_base
    z = residual / MODELO_BASE[ pais ]['scale']  # Standardized residual

    # CDF of the residual (0 to 1)
    cdf = stats.norm.cdf(z)          # P(R ≤ residual)

    # Map CDF to [-100, +100] with inverted sign
    # cdf=0 → +100, cdf=0.5 → 0, cdf=1 → -100
    INDICE_DE_EFICIENCIA =  100 * (1 - 2 * cdf) 


    # -------------------------------------------------
    # 3. PERFIL_DE_EFICIENCIA  (categorical)
    # -------------------------------------------------
    # Example thresholds on the index (adjust as you like)
    if INDICE_DE_EFICIENCIA >= 60:
        PERFIL_DE_EFICIENCIA = "Muy eficiente"
    elif INDICE_DE_EFICIENCIA >= 20:
        PERFIL_DE_EFICIENCIA = "Eficiente"
    elif INDICE_DE_EFICIENCIA >= -20:
        PERFIL_DE_EFICIENCIA = "Moderado"
    elif INDICE_DE_EFICIENCIA >= -60:
        PERFIL_DE_EFICIENCIA = "Ineficiente"
    else:
        PERFIL_DE_EFICIENCIA = "Muy ineficiente"



    if flag_modelo_prestado:
      advertencias.append("El modelo de predicción de consumo eléctrico se ha entrenado con datos de otro país, por lo que la predicción puede no ser precisa para tu hogar.")
    if obs['pais'] in ['CHILE']:
      advertencias.append("Chile se caracteriza por tener hogares con perfiles similares, resultando en un modelo con un poder predictivo relativamente bajo. Por otro lado, las categorias de consumo cuentan con alta precisión.")
    if cantidad_imputaciones_basico > 0:  
      advertencias.append(f"Se realizaron {cantidad_imputaciones_basico} imputación/es en variables clave del modelo, lo que puede afectar la precisión de las predicciones.")
    if cantidad_imputaciones_avanzado > 0:
      advertencias.append(f"Se realizaron {cantidad_imputaciones_avanzado} imputación/es en variables del cuestionario avanzado, lo que puede afectar la precisión de las categorías de consumo.")

    recomendaciones = []
    if PERFIL_DE_CONSUMO in ["Alto", "Muy alto"]:
      recomendaciones.append("Las características de tu hogar (tamaño, clima, cantidad de habitantes) resultan naturalmente en un consumo elevado de electricidad, por otro lado, cambios en hábitos de consumo y la adopción de tecnologías más eficientes tendrán mayor impacto en tu consumo que en otros hogares.")
    elif PERFIL_DE_CONSUMO in ["Bajo", "Muy bajo"]:
      recomendaciones.append("Las características de tu hogar (tamaño, clima, cantidad de habitantes) resultan naturalmente en un consumo bajo, por lo que el impacto de las medidas que tomes se verán en el largo plazo.")
    else:
      recomendaciones.append("Las características de tu hogar (tamaño, clima, cantidad de habitantes) resultan naturalmente en un consumo típico de tu país, donde las medidas de eficiencia energética tendrán un impacto moderado.")

    if PERFIL_DE_EFICIENCIA in ["Ineficiente", "Muy ineficiente"]:
      recomendaciones.append("Tu hogar es ineficiente en comparación con otros hogares de características similares, esto quiere decir que tienes mayores oportunidades de mejorar tu eficiencia energética.")
      recomendaciones.append("Concidera fuentes de energía aternativa como la solar o eólica para reducir los gastos de electricidad.")

    if (vars['AGUA_CALIENTE_electrica'] == 1) :
      recomendaciones.append("Tu hogar tiene calentador de agua eléctrico que representa aproximadamente el {0:.0f}% del consumo total de electricidad, considera usarlo menos y calentar el agua con gas o energía solar.".format(pred_per['AGUA_SANITARIA']))

    if max( pred_per['AIRE_ACONDICIONADO'], pred_per['CALEFACCION'], pred_per['AGUA_SANITARIA']) < 35:
      recomendaciones.append("Muchos electrodomésticos siguen consumiendo electricidad aunque no los estés usando, diversos estudios indican que puede representar hasta un 10% del consumo total del hogar. Considera desconectarlos de la corriente cuando no los uses.")

    if pred_per['AIRE_ACONDICIONADO'] > 10:
      recomendaciones.append("Tu hogar tiene aire acondicionado que representa aproximadamente el {0:.0f}% del consumo total de electricidad, considera usar ventiladores en su lugar o ajustar la temperatura de 75ºF a 78ºF (24º a 26°C) estos pocos grados de diferencia pueden reducir el consumo en hasta un 10%.".format(pred_per['AIRE_ACONDICIONADO']))


    if pred_per['CALEFACCION'] > 10:
      recomendaciones.append("Tu hogar utiliza calefacción eléctrica que representa aproximadamente el {0:.0f}% del consumo total de electricidad, considera ajustar la temperatura a 68ºF (20°C) o incluso menos, cada grado pueden reducir el consumo en un 5%.".format(pred_per['CALEFACCION']))

    if (pred_per['CALEFACCION'] > 10) & (10**vars['DORMITORIOS_log']-1 > 2):
      recomendaciones.append("Recuerda cerrar las puertas de los cuartos que no estés usando para reducir el consumo de calefacción.")


    if (vars['SECARROPAS_electrico'] == 1) & (vars['LAVARROPAS_frecuencia_log'] >= np.log10(2.5) ):
      recomendaciones.append("Tu hogar tiene secarropas eléctrico que representa aproximadamente el {0:.0f}% del consumo total de electricidad, considera usarlo menos y secar la ropa al aire libre.".format(pred_per['SECARROPAS']))

    if (10**vars['VENTANAS_log']-1  > 4*(10**vars['DORMITORIOS_log']-1)):
      recomendaciones.append("Tu hogar tiene una cantidad de ventanas mayor al promedio,  considera mejorar el aislamiento de las ventanas por ejemplo con vidrios de doble acristalamiento.")


    result = {}

    result['salida'] = {
      'Consumo (KWH anual)': CONSUMO,

      'Ranking': RANKING,
      'Ranking interpretacion': RANKING_INTERPRETACION,


      'Consumo esperado para hogares de tus mismas caracterizticas (KWH anual)': 10**logKWH_base,
      'Perfil de consumo': PERFIL_DE_CONSUMO,
      'Probabilidad': CONFIANZA,

      'Indice de eficiencia': INDICE_DE_EFICIENCIA,
      'Perfil de eficiencia': PERFIL_DE_EFICIENCIA,


      'Consumo en calentar agua sanitaria (porcentaje)': pred_per['AGUA_SANITARIA'],
      'Consumo en aire acondicionado (porcentaje)': pred_per['AIRE_ACONDICIONADO'],
      'Consumo en calefaccion (porcentaje)': pred_per['CALEFACCION'],
      'Consumo en cocina (porcentaje)': pred_per['COCINA'],
      'Consumo en refrigeracion (porcentaje)': pred_per['REFRIGERACION'],
      'Consumo en lavado (porcentaje)': pred_per['LAVADO'],
      'Consumo en iluminacion (porcentaje)': pred_per['ILUMINACION'],
      'Consumo en television (porcentaje)': pred_per['TV'],
      'Consumo en otros (porcentaje)': pred_per['OTROS'],

    }
    result['salida_complementaria'] ={
       'advertencias' : advertencias,
       'recomendaciones': recomendaciones
    }


    result['estimacion_financiera'] = { 
      'Gastos estimados en dolares (anual)' : CONSUMO * PRECIO_KWH_PAIS[PAISES[obs['pais']]],
      'Gastos estimados en dolares (mensual)' : CONSUMO * PRECIO_KWH_PAIS[PAISES[obs['pais']]]/12,
      'Tarifa utilizada (US$ por KWH)': PRECIO_KWH_PAIS[PAISES[obs['pais']]]
    }





    return result