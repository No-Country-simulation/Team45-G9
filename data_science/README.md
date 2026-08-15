# MODELO

El modelo actual fue entrenado para Estados Unidos y para Chile. Aunque puede ser utilizado para todos los paises de América. Para Canada utiliza por defecto el modelo de Estados Unidos , para el resto de América utiliza el modelo de Chile.

## Fuentes
Se utilizaron las encuestas RECS 2016 y ENCER 2018.  Complementadas con información externa climática para las distintas provincias/estados ( obtenidas de la EIA, centro meteorológico de Chile y el banco mundial).
Las tarifas eléctricas se obtuvieron de globalpetrolprices.com que publica estudios sobre el costo promedio de la energía para cada país.

## Metodología
Para ambos países se utilizaron modelos de elasticidad completa ponderados. Es decir se aplicó un modelo linear multivariado donde tanto a predictores como respuesta se les aplicó la transformación logaritmo. Se utilizó el factor de expansión como ponderador (es importante notar que esto no habilita el uso de la teoría estadística tradicional, pero si aminora los efectos de la sub/sobre representación en la muestra).

Adicionalmente, se entrenaron modelos logísticos para estimar la proporción de consumo en cada área (calefacción, aire acondicionado, iluminación, etc).

Selección de modelos: Se entrenaron modelos de regresión lineal, random forest y light xgboost  con distintos hiperparámetros. El modelo lineal fue elegido porque se desempeño tan bien como los demás modelos más complejos.

Selección de variables: Se combinaron distintos métodos, tanto una selección manual como un modelo Lasso para descartar variables. Se aplicó la metodología de stability selection (aplicación de muestreo bootstrap y regresión Lasso , identificando que predictores eran seleccionados consistentemente).

Diagnósticos y medidas: Se compararon tanto el R2, error absoluto mediano, junto con gráficos de residuos (histograma, residuos vs predichos, residuos absolutos vs predichos) para garantizar el buen comportamiento del modleo.

Estimación de percentiles: Se utilizó la muestra junto a los factores de expansión para obtener estimaciones de los percentiles que serán utilizados en la salida.

# Entrada de ejemplo

# Salida de ejemplo 


# Recomendaciones basadas en reglas utilizadas en la aplicación (Modelo.py).

Modelo.py devuelve un JSON dividido en tres partes: estimacion_financiera, salida y salida_complementaria.
Dentro de salida_complementaria se encuentran una serie de recomendaciones basadas en el consumo del hogar.
La cantidad de dinero ahorrado se basa en el porcentaje de gasto en la categoría correspondiente, el consumo declarado por el usuario y finalmente el precio promedio de la electricidad para el pais.



| Categoría                             | Cuándo se activa                                                                                                           | Recomendación                                                                                                                         | Ahorro estimado utilizado                                                                                                    |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Agua caliente**                     | El hogar utiliza un calentador de agua eléctrico.                                                                          | Reducir la temperatura del calentador en **10 °C (20 °F)**.                                                                           | Hasta **20%** del consumo de agua caliente.                                                                                  |
| **Aire acondicionado**                | El aire acondicionado representa más del **10% del consumo eléctrico total** del hogar.                                    | Subir el termostato **1 °C (2 °F)** y utilizar un ventilador de techo cuando sea posible.                                             | Hasta **15%** del consumo de aire acondicionado.                                                                             |
| **Calefacción**                       | La calefacción eléctrica representa más del **10% del consumo eléctrico total** del hogar.                                 | Reducir la temperatura de calefacción en **2 °C (4 °F)**.                                                                             | Hasta **20%** del consumo de calefacción.                                                                                    |
| **Calefacción + hogar grande**        | La calefacción representa más del **10% del consumo eléctrico total** y el hogar tiene **más de 2 ambientes/dormitorios**. | Mantener cerrados los ambientes que no estén siendo utilizados para evitar calefaccionar espacios desocupados.                        | No se cuantifica.                                                                                                            |
| **Ventanas**                          | La cantidad de ventanas es superior a **tres veces la cantidad de ambientes/dormitorios** del hogar.                       | Mejorar el aislamiento mediante, por ejemplo, doble acristalamiento, vidrios Low-E o sellado de filtraciones.                         | Las ventanas se consideran responsables de aproximadamente **25%** de la energía utilizada para calefacción y refrigeración. |
| **Lavado / secado de ropa**           | El hogar utiliza un secarropas eléctrico y realiza **al menos 2,5 lavados por semana**.                                    | Siempre que las condiciones lo permitan, secar la ropa al aire libre y reducir el uso del secarropas.                                 | Reducir el uso del secarropas a la mitad → hasta **50%** del consumo asociado al lavado.                                     |
| **Otros consumos**                    | La categoría de otros usos representa más del **25% del consumo eléctrico total**.                                         | Revisar posibles equipos de alto consumo, como bombas de piscina, bombas de riego u otros equipos que funcionan durante varias horas. | No se cuantifica.                                                                                                            |
| **Consumo en standby**                | El hogar no utiliza aire acondicionado, calefacción eléctrica ni calentador de agua eléctrico.                             | Desconectar equipos que continúan consumiendo electricidad aunque estén apagados, especialmente equipos antiguos.                     | Aproximadamente **10% del consumo eléctrico residencial**.                                                                   |
| **Iluminación – LED**                 | La iluminación representa una proporción relevante del consumo eléctrico del hogar.                                        | Reemplazar focos incandescentes o halógenos por iluminación LED.                                                                      | Hasta **90%** del consumo de iluminación.                                                                                    |
| **Iluminación – hábitos**             | La iluminación representa una proporción relevante del consumo eléctrico del hogar.                                        | Aprovechar la iluminación natural y apagar las luces innecesarias.                                                                    | Reducir el uso a la mitad → aproximadamente **50%** del consumo de iluminación.                                              |
| **Refrigeración – mantenimiento**     | La refrigeración representa más del **10% del consumo eléctrico total** del hogar.                                         | Limpiar los serpentines y comprobar que los empaques de las puertas sellen correctamente.                                             | Hasta **30%** del consumo de refrigeración.                                                                                  |
| **Refrigeración – temperatura**       | La refrigeración representa más del **10% del consumo eléctrico total** del hogar.                                         | Mantener el refrigerador a **3 °C (38 °F)** y el congelador a **−18 °C (0 °F)**.                                                      | Cada grado por debajo de estos niveles aumenta el consumo aproximadamente **5%**.                                            |
| **Segundo refrigerador / congelador** | El hogar tiene un congelador o refrigerador adicional.                                                                     | Desconectar los equipos secundarios cuando no sean necesarios, especialmente si son antiguos.                                         | Aproximadamente **400 kWh/año por equipo adicional**.                                                                        |
