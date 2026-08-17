# Ejemplos de uso — API EnergiAI / VólticvS

Fase F del plan de hackathon: mínimo tres ejemplos de utilización, con petición, respuesta e
interpretación. Los tres corrieron contra el servidor real (no son respuestas escritas a mano) y
usan `pais: "BR"` — la tarifa de referencia que especifican las bases (R$ 0,75/kWh).

Los tres son intencionalmente contrastantes: un hogar eficiente, uno moderado, y uno ineficiente,
para mostrar el rango completo de lo que devuelve el clasificador.

---

## Ejemplo 1 — Hogar eficiente

Un dormitorio, una persona, sin climatización eléctrica: el perfil de menor consumo posible dentro de lo que el formulario permite declarar.

**Petición** — `POST /api/analisis-energetico`

```json
{
  "pais": "BR",
  "dormitorios": 1,
  "habitantes_mayores": 1,
  "refrigerador": 1,
  "tv": 1,
  "tv_frecuencia": 10
}
```

**Respuesta real** (recortada a los campos relevantes para la interpretación):

```json
{
  "categoria": "Eficiente",
  "probabilidad": 1.0,
  "fuente_clasificacion": "modelo",
  "consumo_kwh": 71.0,
  "costo_estimado": 53.25,
  "simbolo_moneda": "R$",
  "moneda": "BRL",
  "ahorro_estimado": 0.5,
  "desglose": {
    "Iluminación y uso base por habitantes": 30.0,
    "Refrigerador": 36.0,
    "Televisor": 4.96
  },
  "recomendaciones": [
    "¡Excelente! Tu hogar tiene un consumo eficiente. ¡Sigue así!",
    "Muchos electrodomésticos siguen consumiendo electricidad aunque no los uses (consumo standby) — puede representar hasta un 10% de tu factura. Desconéctalos cuando no los necesites.",
    "Activa el modo ahorro de energía en el TV y evita dejarlo en stand-by durante la noche.",
    "Usa bombillas LED en toda la vivienda — pueden ahorrar hasta un 90% frente a las incandescentes — y aprovecha la luz natural durante el día."
  ],
  "id": "1b363146-19fd-4e2f-b0d3-a6eaa0251192"
}
```

**Interpretación:** el modelo entrenado clasifica este hogar como **Eficiente** con 100.0% de confianza. Con 71.0 kWh/mes, el costo estimado en Brasil es de R$ 53.25 BRL. El desglose muestra que casi todo el consumo viene de iluminación/uso base y el refrigerador — no hay equipos de climatización eléctricos declarados, que es lo que más pesa en los otros dos ejemplos.

---

## Ejemplo 2 — Hogar moderado

Tres dormitorios, tres personas, con aire acondicionado pero sin el resto de los equipos de alto consumo (calefacción, agua caliente, secarropas).

**Petición** — `POST /api/analisis-energetico`

```json
{
  "pais": "BR",
  "dormitorios": 3,
  "ventanas": 7,
  "habitantes_mayores": 3,
  "refrigerador": 1,
  "aire_acondicionado": 1,
  "tv": 2,
  "tv_frecuencia": 18,
  "lavado_frecuencia": 4
}
```

**Respuesta real** (recortada a los campos relevantes para la interpretación):

```json
{
  "categoria": "Moderado",
  "probabilidad": 0.5943,
  "fuente_clasificacion": "modelo",
  "consumo_kwh": 279.2,
  "costo_estimado": 209.4,
  "simbolo_moneda": "R$",
  "moneda": "BRL",
  "ahorro_estimado": 1.4,
  "desglose": {
    "Aire acondicionado": 119.39,
    "Iluminación y uso base por habitantes": 90.0,
    "Lavadora de ropa": 17.14,
    "Refrigerador": 36.0,
    "Televisor": 16.71
  },
  "recomendaciones": [
    "Tu consumo es moderado. Con pequeños ajustes puedes alcanzar la categoría Eficiente.",
    "Tu aire acondicionado representa aproximadamente el 43% de tu consumo. Subir el termostato 1°C (2°F) y usar un ventilador de techo puede reducir hasta un 15% ese consumo.",
    "Activa el modo ahorro de energía en el TV y evita dejarlo en stand-by durante la noche.",
    "Usa bombillas LED en toda la vivienda — pueden ahorrar hasta un 90% frente a las incandescentes — y aprovecha la luz natural durante el día."
  ],
  "id": "7e10642c-cd40-49f2-a887-dfa85216ffbe"
}
```

**Interpretación:** con aire acondicionado ya en la ecuación pero sin el resto de los equipos de alto consumo, el modelo lo ubica en **Moderado** — a mitad de camino, con 59.4% de confianza (más baja que en los otros dos casos, coherente con estar en la categoría intermedia, más cerca de las fronteras de decisión que los casos extremos).

---

## Ejemplo 3 — Hogar ineficiente

Cuatro dormitorios, seis personas, con todos los equipos de climatización eléctricos a la vez más un segundo refrigerador y freezer — el escenario de mayor consumo.

**Petición** — `POST /api/analisis-energetico`

```json
{
  "pais": "BR",
  "dormitorios": 4,
  "ventanas": 14,
  "habitantes_mayores": 4,
  "habitantes_menores": 2,
  "refrigerador": 2,
  "freezer": 1,
  "aire_acondicionado": 1,
  "calefaccion_electrica": 1,
  "agua_caliente_electrica": 1,
  "secarropas_electrico": 1,
  "horno_electrico": 1,
  "tv": 3,
  "tv_frecuencia": 28,
  "lavado_frecuencia": 5
}
```

**Respuesta real** (recortada a los campos relevantes para la interpretación):

```json
{
  "categoria": "Ineficiente",
  "probabilidad": 1.0,
  "fuente_clasificacion": "modelo",
  "consumo_kwh": 843.9,
  "costo_estimado": 632.92,
  "simbolo_moneda": "R$",
  "moneda": "BRL",
  "ahorro_estimado": 1.7,
  "desglose": {
    "Aire acondicionado": 119.39,
    "Calefactor eléctrico": 148.5,
    "Congeladora / freezer": 44.64,
    "Horno eléctrico": 30.09,
    "Iluminación y uso base por habitantes": 150.0,
    "Lavadora de ropa": 21.43,
    "Refrigerador": 72.0,
    "Secadora de ropa": 40.07,
    "Televisor": 37.8,
    "Termotanque / calentador de agua electrico": 180.0
  },
  "recomendaciones": [
    "Tu consumo es elevado. Implementa las recomendaciones para reducirlo significativamente.",
    "Tu calentador de agua eléctrico representa aproximadamente el 21% de tu consumo total. Reducir su temperatura en 10°C (20°F) puede ahorrar hasta un 20% de ese consumo.",
    "Muchos electrodomésticos siguen consumiendo electricidad aunque no los uses (consumo standby) — puede representar hasta un 10% de tu factura. Desconéctalos cuando no los necesites.",
    "Tu aire acondicionado representa aproximadamente el 14% de tu consumo. Subir el termostato 1°C (2°F) y usar un ventilador de techo puede reducir hasta un 15% ese consumo.",
    "Tu calefacción eléctrica representa aproximadamente el 18% de tu consumo. Bajar la temperatura 2°C (4°F) puede ahorrar hasta un 20% de ese consumo.",
    "Mantén cerrados los ambientes que no estés usando, para no calefaccionar espacios vacíos.",
    "Tu secarropas eléctrico representa aproximadamente el 5% de tu consumo. Secar la ropa al aire libre en vez de usarlo puede ahorrar hasta un 50% de ese consumo.",
    "Tu vivienda tiene más ventanas de lo habitual para su tamaño — pueden ser responsables de hasta un 25% de la energía usada en calefacción y refrigeración. Mejorar el aislamiento (doble vidriado, sellado de filtraciones) ayuda a reducirlo."
  ],
  "id": "7f38b221-451e-4366-8c49-55ca2ea59ca4"
}
```

**Interpretación:** con los cinco equipos de climatización eléctricos activos a la vez más un segundo refrigerador y freezer, el consumo sube a 843.9 kWh/mes — el modelo lo clasifica como **Ineficiente** con 100.0% de confianza. Las recomendaciones que devuelve el sistema apuntan directo a los equipos que más pesan en el desglose.

---

## Nota sobre la tarifa usada

Las bases especifican una tarifa de referencia de R$ 0,75/kWh para Brasil. El motor de cálculo usa
la tarifa real de `data/consumo_referencia.json` para cada país — para Brasil, ese valor coincide
exactamente con el de las bases (confirmado en la Fase C: `consumo_kwh: 420` con `pais: "BR"` da
`costo_estimado_mensual: 315.0`, que es 420 × 0,75).

## Cómo reproducir estos ejemplos

Los tres corrieron contra el servidor real, con el modelo entrenado (Fase A/B) ya cargado:

```bash
curl -X POST http://localhost:5000/api/analisis-energetico \
  -H "Content-Type: application/json" \
  -d '{"pais":"BR","dormitorios":1,"habitantes_mayores":1,"refrigerador":1,"tv":1,"tv_frecuencia":10}'
```

Cada respuesta incluye un `id` — se puede consultar de nuevo con
`GET /api/analisis-energetico/{id}` (Fase D), o ver los últimos análisis con
`GET /api/analisis-energetico`.
