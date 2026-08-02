# ⚡ VólticvS — Asesor Energético con IA
### Team 45 · Oracle ONE G9 · No-Country Simulation

Asesor de eficiencia energética que analiza el perfil de consumo del hogar, clasifica su eficiencia, estima costos y genera recomendaciones personalizadas.

---

## Arquitectura

Frontend (HTML/CSS/JS)
↓
Flask API (Python) — puerto 5000
├── /api/analisis-energetico ← spec oficial del hackathon
├── /api/calcular ← motor rico por artefacto
└── /api/paises ← tarifas por país
↓
Groq (llama-3.1-8b-instant) — solo redacta la narrativa final


El LLM nunca calcula números. Todo el consumo y ahorro se calcula con Python puro (determinista). El modelo solo convierte los resultados en texto natural.

---

## Stack

- **Backend:** Python 3.12, Flask, LangChain
- **LLM:** Groq — llama-3.1-8b-instant (gratuito)
- **Frontend:** HTML5, CSS3, JavaScript ES6+
- **Deploy:** OCI Compute (Always Free), systemd

---

## Instalación local

```bash
git clone https://github.com/Saigon117/Team45-G9-unified
cd Team45-G9-unified/app
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # agregar GROQ_API_KEY
python app.py
```

Abre http://localhost:5000

API key gratuita en: https://console.groq.com/keys

---

## Endpoints

### `POST /api/analisis-energetico`
Spec oficial del hackathon.

**Request:**
```json
{
  "consumo_kwh": 420,
  "uso_horario_pico": true,
  "cantidad_equipos": 10,
  "tipo_inmueble": "Casa",
  "horas_alto_consumo": 8
}
```

**Response:**
```json
{
  "categoria": "Ineficiente",
  "probabilidad": 0.84,
  "recomendaciones": [
    "Reducir el uso de equipos durante los horarios pico",
    "Evaluar equipos con alto consumo energético",
    "Distribuir las actividades de mayor consumo a lo largo del día"
  ],
  "costo_estimado_mensual": 315.0
}
```

### `POST /api/calcular`
Motor de cálculo detallado por artefacto (electrodomésticos, iluminación, standby).

### `GET /api/paises`
Lista de países con tarifas eléctricas de referencia.

---

## Estructura del proyecto

Team45-G9-unified/
├── app/ # Aplicación principal
│ ├── app.py # Servidor Flask + endpoints
│ ├── src/
│ │ ├── calculos.py # Motor determinista de consumo
│ │ ├── agente.py # Agente LangChain (CLI)
│ │ └── tools.py # Tools del agente
│ ├── templates/ # Frontend (Jean)
│ ├── static/ # CSS + JS
│ └── data/ # Datos de referencia
├── data-science/ # Notebooks y modelos ML
└── bases/ # Datasets


---

## Equipo

- **Alejandro** — Backend, motor de cálculo, deploy OCI
- **Jean** — Frontend, UX, diseño
- **Héctor** — Integración, arquitectura unificada

---

## Estado del MVP

- [x] Motor de cálculo determinista por artefacto
- [x] Endpoint spec oficial `/api/analisis-energetico`
- [x] Interfaz web con tabs por categoría
- [x] Selector de país con tarifas de referencia
- [x] Narrativa generada por LLM (Groq)
- [x] Deploy en OCI Compute
- [ ] Spring Boot como capa API (próximo paso)
- [ ] Integración con modelo ML de data-science/
