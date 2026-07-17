# Team45-G9

Nuestro Espacio para nuestro Team N45


## Resultados esperados

### Ciencia de Datos

Notebook que contenga:
- Exploración y limpieza de datos (EDA);
- Análisis de patrones de consumo;
- Procesamiento y transformación de variables;
- Entrenamiento de modelos supervisados;
- Evaluación utilizando métricas adecuadas;
- Generación de recomendaciones basadas en reglas o modelos;
- Serialización del modelo entrenado.


### Back-End

API REST que contenga:

- Endpoint para análisis del consumo;
- Endpoint para consulta de resultados;
- Validación de entrada;
- Manejo de errores;
- Documentación de los endpoints.


### OCI

Uso de al menos uno de los siguientes servicios:
- Object Storage para almacenamiento de modelos o datos;
- OCI Compute para el alojamiento de la API;
- OCI Functions para procesamiento específico;
- Base de datos opcional para persistencia.
- Funcionalidades obligatorias (MVP)

### Análisis del perfil energético

**Endpoint**:

POST /analisis-energetico

**Entrada**:
```
{
  "consumo_kwh": 420,
  "uso_horario_pico": true,
  "cantidad_equipos": 10,
  "tipo_inmueble": "Casa",
  "horas_alto_consumo": 8
}
```
**Salida**:
```
{
  "categoria": "Ineficiente",
  "probabilidad": 0.81
}
```

**Recomendaciones de optimización**

- Salida complementaria:
```
{
  "recomendaciones": [
    "Reducir el uso de equipos durante los horarios pico",
    "Evaluar equipos con alto consumo energético",
    "Distribuir las actividades de mayor consumo a lo largo del día"
  ]
}
```

- Estimación financiera

Utilizando la tarifa de referencia sugerida de $ 0,75 por kWh:
```
{
  "costo_estimado_mensual": 315.00
}
```

### Requisitos mínimos

- Modelo entrenado y cargado correctamente;
- Clasificación funcional;
- Generación de recomendaciones;
- Estimación del costo energético;
- API documentada;
- Integración con OCI;
- Mínimo de tres ejemplos reales o simulados de uso.


### Recursos opcionales

- Dashboard de seguimiento;
- Historial de análisis;
- Procesamiento por lotes mediante CSV;
- Containerización con Docker;
- Pruebas automatizadas;
- Alertas de alto consumo;
- Visualizaciones gráficas;
- Comparación entre períodos;
- Ranking de eficiencia energética;
- Simulación de escenarios de ahorro.



## Directrices para Ciencia de Datos

Cada equipo deberá construir su propia base de datos relacionada con el consumo energético.

Los datos podrán ser:
- Recopilados de fuentes públicas;
- Obtenidos de bases de datos abiertas;
- Generados manualmente por el equipo;
- Simulados para representar diferentes perfiles de consumo.

Se recomienda utilizar:
- Python;
- Pandas;
- Scikit-Learn;
- Regresión Logística;
- Random Forest;
- Árboles de Decisión.
- Se permite el uso de otros modelos.

Los equipos deberán definir y justificar los criterios utilizados para caracterizar los diferentes perfiles de eficiencia energética.


## Directrices para Back-End

La solución deberá poner a disposición una API REST desarrollada preferentemente en Java con Spring Boot.

La API deberá:
- Recibir los datos de consumo;
- Ejecutar el análisis;
- Devolver la clasificación, probabilidad y recomendaciones;
- Devolver respuestas en formato JSON;
- Implementar validaciones y manejo de errores.
- La arquitectura elegida deberá ser documentada por el equipo.


## OCI

La solución debe utilizar al menos un servicio OCI como parte obligatoria del proyecto.

Sugerencias:
- Object Storage para almacenamiento de modelos o archivos;
- OCI Compute para el despliegue de la API;
- OCI Functions para procesamiento complementario;
- Base de datos opcional para persistencia.


## Front-End (opcional)

Opcionalmente, el equipo podrá desarrollar una interfaz sencilla para:
- Ingreso de información de consumo;
- Visualización de los resultados del análisis;
- Visualización de recomendaciones;
- Presentación de gráficos e indicadores.

El desarrollo del Front-End no es obligatorio para el MVP.
