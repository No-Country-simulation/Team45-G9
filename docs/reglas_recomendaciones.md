# Reglas de recomendaciones — fuente de datacience

Tabla de referencia entregada por el equipo de datacience (2026-08-15), usada para portar la
lógica de recomendaciones del motor estadístico de G9 (`src/modelo.py`) al motor de
`app.py::_recomendaciones_contextuales()`.

**Corrección aplicada:** el umbral de ventanas en el código original de G9 usaba 4× dormitorios;
esta tabla (más reciente) especifica 3×. Se usó 3×, el valor de esta tabla.

| Categoría | Cuándo se activa | Recomendación | Ahorro estimado utilizado |
|---|---|---|---|
| Agua caliente | El hogar utiliza un calentador de agua eléctrico. | Reducir la temperatura del calentador en 10 °C (20 °F). | Hasta 20% del consumo de agua caliente. |
| Aire acondicionado | El aire acondicionado representa más del 10% del consumo eléctrico total del hogar. | Subir el termostato 1 °C (2 °F) y utilizar un ventilador de techo cuando sea posible. | Hasta 15% del consumo de aire acondicionado. |
| Calefacción | La calefacción eléctrica representa más del 10% del consumo eléctrico total del hogar. | Reducir la temperatura de calefacción en 2 °C (4 °F). | Hasta 20% del consumo de calefacción. |
| Calefacción + hogar grande | La calefacción representa más del 10% del consumo eléctrico total y el hogar tiene más de 2 ambientes/dormitorios. | Mantener cerrados los ambientes que no estén siendo utilizados para evitar calefaccionar espacios desocupados. | No se cuantifica. |
| Ventanas | La cantidad de ventanas es superior a **tres** veces la cantidad de ambientes/dormitorios del hogar. | Mejorar el aislamiento mediante, por ejemplo, doble acristalamiento, vidrios Low-E o sellado de filtraciones. | Las ventanas se consideran responsables de aproximadamente 25% de la energía utilizada para calefacción y refrigeración. |
| Lavado / secado de ropa | El hogar utiliza un secarropas eléctrico y realiza al menos 2,5 lavados por semana. | Siempre que las condiciones lo permitan, secar la ropa al aire libre y reducir el uso del secarropas. | Reducir el uso del secarropas a la mitad → hasta 50% del consumo asociado al lavado. |
| Otros consumos | La categoría de otros usos representa más del 25% del consumo eléctrico total. | Revisar posibles equipos de alto consumo, como bombas de piscina, bombas de riego u otros equipos que funcionan durante varias horas. | No se cuantifica. *(pendiente de portar — no hay categoría "otros" en el desglose actual)* |
| Consumo en standby | El hogar no utiliza aire acondicionado, calefacción eléctrica ni calentador de agua eléctrico. | Desconectar equipos que continúan consumiendo electricidad aunque estén apagados, especialmente equipos antiguos. | Aproximadamente 10% del consumo eléctrico residencial. |
| Iluminación – LED | La iluminación representa una proporción relevante del consumo eléctrico del hogar. | Reemplazar focos incandescentes o halógenos por iluminación LED. | Hasta 90% del consumo de iluminación. |
| Iluminación – hábitos | La iluminación representa una proporción relevante del consumo eléctrico del hogar. | Aprovechar la iluminación natural y apagar las luces innecesarias. | Reducir el uso a la mitad → aproximadamente 50% del consumo de iluminación. |
| Refrigeración – mantenimiento | La refrigeración representa más del 10% del consumo eléctrico total del hogar. | Limpiar los serpentines y comprobar que los empaques de las puertas sellen correctamente. | Hasta 30% del consumo de refrigeración. *(pendiente de portar)* |
| Refrigeración – temperatura | La refrigeración representa más del 10% del consumo eléctrico total del hogar. | Mantener el refrigerador a 3 °C (38 °F) y el congelador a −18 °C (0 °F). | Cada grado por debajo de estos niveles aumenta el consumo aproximadamente 5%. *(pendiente de portar)* |
| Segundo refrigerador / congelador | El hogar tiene un congelador o refrigerador adicional. | Desconectar los equipos secundarios cuando no sean necesarios, especialmente si son antiguos. | Aproximadamente 400 kWh/año por equipo adicional. |

## Estado de la implementación

Portadas a `_recomendaciones_contextuales()`: agua caliente, aire acondicionado, calefacción,
calefacción + hogar grande, ventanas (corregido a 3x), lavado/secado, standby, segundo
refrigerador/congelador, iluminación LED (genérica, sin condición de activación propia).

**Pendientes** (la fila lo indica): "otros consumos" (no existe esa categoría en el desglose de
`calculos.py` todavía) y las dos reglas de refrigeración con condición de activación específica
(hoy solo está la regla de "segundo refrigerador", no las de mantenimiento/temperatura).
