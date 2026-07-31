# Este código simula el uso de un modelo, tanto el input, su limpeza, las estimaciones, la creación de gráficos y creación de un JSON de resultado

import json
import numpy as np
'''
obs = {
    'pais' : 'USA',
    'estado' : 'NY',
    'dormitorios' : 1,
    'tamano': 500,
    'ventanas': 2,
    'agua_caliente_electrica':0,
    'agua_caliente_tamano': 30,
    'calefaccion_electrica' : 0,
    'lavarropas_frecuencia' : 7,
    'secarropas_electrico' : 0,
    'aire_acondicionado' : 2,
    'tv_cantidad' : 1,
    'freezer' : 0,
    'refrigerador': 1,
    'luces_exterior':0,
    'luces_interior_4_horas': 3,
    'kwh': 2000,
    'periodo_anual': 1



}
'''

#IMPORTA

with open("INPUT.json", "r", encoding="utf-8") as file:
    obs = json.load(file)

# PRECIOS
PRECIO_KWH_PAIS ={
    'Afghanistan' : 0.052,
'Albania' : 0.119,
'Algeria' : 0.041,
'Andorra' : 0.196,
'Angola' : 0.016,
'Argentina' : 0.087,
'UK' : 0.402,
'Ukraine' : 0.084,
'Uruguay' : 0.255,
'USA' : 0.188,
'Uzbekistan' : 0.039,
'Venezuela' : 0.069,
'Vietnam' : 0.078,
'Zambia' : 0.023,
}
# REGIONES
REGION = {}

REGION['USA'] ={
    "AL": "east_south_central",
    "AK": "pacific",
    "AZ": "mountain_south",
    "AR": "west_south_central",
    "CA": "pacific",
    "CO": "mountain_north",
    "CT": "new_england",
    "DE": "south_atlantic",
    "FL": "south_atlantic",
    "GA": "south_atlantic",
    "HI": "pacific",
    "ID": "mountain_north",
    "IL": "east_north_central",
    "IN": "east_north_central",
    "IA": "west_north_central",
    "KS": "west_north_central",
    "KY": "east_south_central",
    "LA": "west_south_central",
    "ME": "new_england",
    "MD": "south_atlantic",
    "MA": "new_england",
    "MI": "east_north_central",
    "MN": "west_north_central",
    "MS": "east_south_central",
    "MO": "west_north_central",
    "MT": "mountain_north",
    "NE": "west_north_central",
    "NV": "mountain_south",
    "NH": "new_england",
    "NJ": "mid_atlantic",
    "NM": "mountain_south",
    "NY": "mid_atlantic",
    "NC": "south_atlantic",
    "ND": "west_north_central",
    "OH": "east_north_central",
    "OK": "west_south_central",
    "OR": "pacific",
    "PA": "mid_atlantic",
    "RI": "new_england",
    "SC": "south_atlantic",
    "SD": "west_north_central",
    "TN": "east_south_central",
    "TX": "west_south_central",
    "UT": "mountain_south",
    "VT": "new_england",
    "VA": "south_atlantic",
    "WA": "pacific",
    "WV": "south_atlantic",
    "WI": "east_north_central",
    "WY": "mountain_north",
    "DC": "south_atlantic"
}

# ERROR DEL MODELO
ERROR_MODELO = {'USA':0.186}

# MODELOS
MODELOS = {}

MODELOS['USA'] = {
  'INTERCEPTO' :  2.9194,
  'DORMITORIOS_log' :  0.1817,
  'TAMANO_sqft_log' : 0.0935,
  'VENTANAS_log' : 0.0720,

  'AGUA_CALIENTE_electrica' :0.1041, 
  'AGUA_CALIENTE_tamano' : 0.0009,

  'CALEFACCION_electrico' : 0.1294, 
  'LAVARROPAS_frecuencia_log' :  0.1069 ,
  'SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log' : 0.0717 ,
 'DIVISION_hot_x_AIRE_ACONDICIONADO' : 0.1242,
  'TV_log' : 0.2182,
 'FREEZER_log' : 0.2198,
  'LUCES_afuera_log_X_LUCES_4_horas_log': 0.0784,
  'REFRIGERADOR_log': 0.3309    
}
  

vars = {}
division = REGION[obs['pais']][obs['estado']]
hot = int( division  in ['south_atlantic', 'east_south_central', 'west_south_central', 'west_south_central', 'mountain_south']  )
vars['INTERCEPTO'] = 1
vars['DORMITORIOS_log'] =  np.log( 1 + obs['dormitorios'] )
vars['TAMANO_sqft_log'] = np.log( 1 + obs['tamano'] )
vars['VENTANAS_log'] = np.log( 1 + obs['ventanas'] )
vars['AGUA_CALIENTE_electrica'] =  obs['agua_caliente_electrica']
vars['AGUA_CALIENTE_tamano'] =  obs['agua_caliente_tamano']
vars['CALEFACCION_electrico'] =  obs['calefaccion_electrica']
vars['LAVARROPAS_frecuencia_log'] =  np.log( 1 + obs['lavarropas_frecuencia'] )
vars['SECARROPAS_electrico_X_LAVARROPAS_frecuencia_log'] =  np.log( 1 +   obs['lavarropas_frecuencia']) * obs['secarropas_electrico'] 
vars['DIVISION_hot_x_AIRE_ACONDICIONADO'] = hot* int( obs['aire_acondicionado'] in [1,2,3] )
vars['TV_log'] =  np.log( 1 + obs['tv_cantidad'] )
vars['FREEZER_log'] =  np.log( 1 + obs['freezer'] )
vars['LUCES_afuera_log_X_LUCES_4_horas_log'] =  np.log( 1 + obs['luces_exterior'] * obs['luces_interior_4_horas'] )
vars['REFRIGERADOR_log'] =  np.log( 1 + obs['refrigerador'] )

logKWH = 0
for var in list(MODELOS[ obs['pais'] ].keys() ):
  logKWH +=  MODELOS[ obs['pais'] ][var] * vars[var]

                                                                                
if obs['periodo_anual']:
  consumo = obs['kwh']
else:
  consumo = 12*obs['kwh']
                                                                                
result = {
  'KWH observados': consumo,
  'KWH estimados': 10**logKWH,
  'Eficiencia': (np.log10(1+consumo) - logKWH) / ERROR_MODELO[obs['pais']],
  'gastos estimados en dolares' : 10**logKWH * PRECIO_KWH_PAIS[obs['pais']]
}

with open("OUTPUT.json", "w", encoding="utf-8") as file:
    json.dump(result, file, indent=4, ensure_ascii=False)
