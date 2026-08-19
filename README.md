# ⚡ VólticvS — Asesor Energético Inteligente

Plataforma web para diagnosticar el consumo eléctrico de un hogar, estimar su ahorro potencial y dar
recomendaciones concretas. Soporta **24 países** de América y España, cada uno con su moneda y tarifa.

> **Los números son deterministas.** El cálculo lo hace [`src/calculos.py`](src/calculos.py) con
> física básica —potencia × tiempo, calor específico del agua— y el modelo de lenguaje **solo redacta
> la narrativa y lee las boletas**. Ningún importe sale de un LLM. Esta separación es deliberada:
> evita que el sistema alucine cifras de ahorro.

**Contexto.** Responde a las bases del hackathon *EnergiAI – Inteligencia para el Consumo
Energético*, versionadas en [`docs/EnergiAI.pdf`](docs/EnergiAI.pdf).

> ✅ **Cumple los entregables obligatorios.** Modelo supervisado entrenado
> ([`notebooks/energiai.ipynb`](notebooks/energiai.ipynb), Regresión Logística elegida por evidencia
> sobre Random Forest — ver el propio notebook para la comparación) y persistencia en Object Storage
> de OCI ([`src/oci_storage.py`](src/oci_storage.py), con degradación explícita si no hay
> credenciales). El estado punto por punto, y lo poco que queda de pulido, están en
> [`docs/PLAN-HACKATHON.md`](docs/PLAN-HACKATHON.md). Ejemplos reales de uso —tres casos
> contrastantes, corridos contra el servidor, no escritos a mano— en
> [`docs/EJEMPLOS.md`](docs/EJEMPLOS.md).

---

## Arranque rápido

### Con Docker (recomendado)

```bash
git clone https://github.com/alejolanda/desafioTeam49.git
cd desafioTeam49
cp .env.example .env      # y edita las claves, ver más abajo
docker compose up --build
```

La app queda en **http://localhost:5000**.

> **En macOS el puerto 5000 lo ocupa el receptor de AirPlay.** Usa otro puerto para el host sin tocar
> el interno: `HOST_PORT=5001 docker compose up`, o desactiva *Ajustes → General → AirDrop y Handoff →
> Receptor AirPlay*.

El código va montado en solo lectura con recarga automática: al editar `app.py` o `src/`, gunicorn se
reinicia solo. Para todo lo demás, ver [Comandos](#comandos) al final.

### Sin Docker

Requiere **Python 3.12+**.

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

---

## Configuración

Todas las variables viven en `.env`, que **nunca** se versiona ni entra en la imagen de Docker.
[`.env.example`](.env.example) las documenta una a una; estas son las que importan:

| Variable | Qué hace | ¿Obligatoria? |
|---|---|---|
| `GROQ_API_KEY` | Narrativa y lectura de boletas | No, pero sin ella se degrada |
| `NOMINATIM_CONTACTO` | Correo de contacto del equipo | Para detectar la ubicación |
| `GROQ_TIMEOUT_S` | Segundos antes de abandonar una llamada al modelo | No (10) |
| `RATELIMIT_STORAGE_URI` | Redis, si se usa más de un worker | No (memoria) |
| `ENABLE_API_DOCS` | Sirve el contrato en `/openapi.yaml` | No (apagado) |
| `HOST_PORT` | Puerto del host, separado del interno | No (5000) |
| `INSTALAR_DOCS` | Mete Swagger UI en la imagen al construirla | No (0) |
| `FLASK_DEBUG` | **Dejar en 0.** El depurador de Werkzeug permite ejecución remota de código | No (0) |

**La aplicación funciona sin ninguna clave.** Sin `GROQ_API_KEY` el diagnóstico se calcula igual —es
determinista— y la narrativa cae a un texto de respaldo, marcado como tal en el campo
`narrativa_fuente`. Sin `NOMINATIM_CONTACTO` no se detecta la ubicación y se pide a mano; es
deliberado: su política de uso exige identificar la aplicación, y es preferible perder la función
antes que hacer peticiones sin identificar contra un servicio comunitario gratuito.

---

## Cómo funciona

```mermaid
flowchart TB
    subgraph navegador["Navegador"]
        UI["index.html + app.js<br/>asistente de 4 pasos"]
        Denji["denji.js<br/>guía por voz y rellena el formulario"]
    end

    subgraph flask["Flask · app.py"]
        Calculos["src/calculos.py<br/>MOTOR DETERMINISTA<br/>kWh, costo y ahorro salen de aquí"]
        Modelo["src/modelo.py<br/>MODELO ENTRENADO<br/>categoría + probabilidad real"]
        LLM["src/llm.py<br/>acceso a Groq<br/>timeout, validación, degradación"]
        Geo["src/geo.py<br/>intermediario ante OpenStreetMap"]
        Almacen["src/almacen.py<br/>historial en SQLite"]
    end

    Datos[("data/consumo_referencia.json<br/>fuente única: potencias, tarifas<br/>y suposiciones de uso")]
    OCI[("OCI Object Storage<br/>modelo entrenado serializado<br/>opcional, con degradación")]

    UI -->|JSON| flask
    Denji -->|rellena| UI
    Calculos --> Datos
    Geo --> Datos
    Modelo -.->|"si no hay local,<br/>lo descarga una vez"| OCI
    LLM -.->|"solo redacta y lee boletas<br/>ningún importe"| Calculos
    flask --> Almacen
```

El modelo de lenguaje **nunca calcula**: recibe cifras ya cerradas por `calculos.py` y solo las
redacta. La categoría y su probabilidad, en cambio, sí salen de un modelo entrenado —
`src/modelo.py` (Fase A/B del plan de hackathon), no de umbrales fijos ni de un LLM. Si el archivo
del modelo no está disponible ni en local ni en OCI, se degrada a umbrales y lo declara en
`fuente_clasificacion`.

### Infraestructura

```mermaid
flowchart TB
    Cliente["Navegador<br/>localhost:HOST_PORT"]

    subgraph maquina["Tu máquina"]
        Env[".env<br/>inyectado al crear el contenedor"]
        Fuente["código fuente<br/>montado en solo lectura"]

        subgraph contenedor["Contenedor · python:3.12-slim · usuario sin privilegios"]
            Gunicorn["gunicorn<br/>1 worker · 8 hilos · timeout 60 s"]
            App["Flask"]
            Tmp[("/app/uploads<br/>tmpfs, en memoria<br/>las boletas no tocan disco")]
        end
    end

    subgraph fuera["Servicios externos"]
        Groq["Groq<br/>narrativa y lectura de boletas"]
        OSM["Nominatim · OpenStreetMap<br/>geocodificación inversa"]
    end

    Cliente -->|"HOST_PORT → 5000"| Gunicorn
    Gunicorn --> App
    App -->|"borrada al terminar"| Tmp
    Env -.-> App
    Fuente -.->|"recarga automática"| Gunicorn
    App -.->|"timeout 10 s · 1 reintento<br/>degrada si falla"| Groq
    App -.->|"1 petición/s · con caché<br/>solo si hay contacto configurado"| OSM
```

Las flechas punteadas son **opcionales**: si Groq o Nominatim no responden, o no están configurados,
la aplicación sigue funcionando con menos prestaciones. El diagnóstico nunca depende de ellos.

Un solo worker con hilos, y no varios procesos, porque el límite de tasa y la caché de
geocodificación viven en la memoria del proceso. Escalar exige antes apuntar `RATELIMIT_STORAGE_URI`
a Redis.

### Construcción y entrega

```mermaid
flowchart LR
    Commit["commit / PR"] --> CI["GitHub Actions"]
    CI --> Lint["ruff"]
    CI --> Tests["pytest"]
    CI --> Build["docker build"]
    Build --> Sonda["arranca y sondea /health"]
    Build --> Secretos["verifica que no haya .env ni .zip"]

    subgraph imagen["Imagen · 2 etapas"]
        Builder["builder<br/>compila desde requirements.lock<br/>53 paquetes fijados"]
        Runtime["runtime<br/>sin compiladores · 288 MB"]
        Builder -->|"copia /opt/venv"| Runtime
    end

    Build --> imagen
```

### Dos formas de estimar el consumo

1. **Declarado.** Escribes los kWh de tu boleta, o la subes y se extraen solos.
2. **Estimado.** Declaras tu equipamiento y se calcula artefacto por artefacto.

Si no das ninguno de los dos, el resultado es 0 con `fuente_consumo: "sin_datos"`. No se inventa una
cifra de relleno.

### De dónde sale el ahorro

De la suma real del consumo evitable de cada artefacto: lo que gasta un equipo en modo de espera
frente a lo que gastaría desconectado. Se calcula siempre, incluso cuando declaras el consumo de tu
boleta, porque sin desglose no hay forma de saber dónde está el ahorro.

> **Limitación conocida.** Hoy solo se monetiza el consumo fantasma. Las recomendaciones textuales
> sugieren ahorros mayores —bajar el aire acondicionado a 24 °C, lavar en frío, cambiar a LED— y
> ninguno de ellos entra todavía en la cifra. El `ahorro_estimado` es, por tanto, conservador.

### El modelo entrenado (Fase A/B)

La categoría de eficiencia (`Eficiente` / `Moderado` / `Ineficiente`) y su `probabilidad` salen de un
modelo supervisado real, no de umbrales fijos ni de un LLM:

- **Dataset:** sintético, generado con semilla fija (`scripts/generar_dataset.py`) muestreando
  perfiles de hogar plausibles y calculando su consumo con el motor físico real del proyecto
  (`calculos.estimar_desde_perfil`) — no es ruido aleatorio, es internamente coherente con lo que la
  API ya calcula.
- **Notebook:** [`notebooks/energiai.ipynb`](notebooks/energiai.ipynb), con las seis secciones que
  piden las bases (EDA, patrones, transformación de variables, entrenamiento, evaluación,
  serialización). Corre de principio a fin sin intervención.
- **Modelo elegido por evidencia, no por preferencia inicial:** el plan proponía Random Forest con
  Regresión Logística como línea base. En la práctica, la Regresión Logística ganó (97,3% de
  exactitud contra 91,7% del Random Forest ya ajustado) — el motor calcula el consumo como una suma
  lineal de watts × horas × frecuencia, así que un modelo lineal le queda mejor a este problema. El
  notebook documenta la comparación completa.
- **Serialización:** `modelos/clasificador_energetico.joblib` + `modelos/metadatos.json` (versión de
  scikit-learn, fecha, métricas, y el orden exacto de las features — sin esto último, un
  reordenamiento futuro de columnas produce predicciones erróneas en silencio).
- **Degradación:** si `modelos/clasificador_energetico.joblib` no existe (clon que no corrió el
  notebook, o antes de que Fase E lo descargue de OCI), `src/modelo.py` cae a los umbrales fijos
  anteriores (250 / 450 kWh) y lo declara en `fuente_clasificacion: "umbrales"` — nunca se inventa
  una probabilidad sin un modelo real detrás.

### Integración con OCI (Fase E)

El modelo entrenado se descarga desde **OCI Object Storage** al arrancar, si no está ya en local
(`src/oci_storage.py`). Autenticación en dos niveles:

1. **Instance Principal** — sin ninguna clave que gestionar, porque la API ya se aloja en una VM de
   OCI Compute. Requiere un *dynamic group* + *policy* con permiso de lectura sobre el bucket,
   configurado en la consola de OCI (infraestructura, no código).
2. **Config-file** (`~/.oci/config`) — para desarrollo local, en una máquina que no es una VM de OCI.

Sin ninguna de las dos credenciales disponibles, o sin `OCI_BUCKET_NAMESPACE`/`OCI_BUCKET_NAME`
configurados, la app **no intenta conectarse** y usa el modelo que ya tenga en local — mismo
espíritu que la degradación de Nominatim. El estado real (si está configurado, si el modelo vino de
OCI o de local) se puede ver en `GET /health`.

---

## API

El contrato completo está en [`docs/openapi.yaml`](docs/openapi.yaml). Con `ENABLE_API_DOCS=1` se
sirve además en `/openapi.yaml`.

La interfaz visual de Swagger en `/apidocs` no viaja en la imagen por defecto —son ~9 MB de activos
que no pintan nada en producción, donde además la documentación va apagada. Para levantarla:

```bash
INSTALAR_DOCS=1 docker compose build && docker compose up -d   # con Docker
pip install -r requirements-dev.txt                            # sin Docker
```

y `ENABLE_API_DOCS=1` en el `.env`.

| Método | Ruta | Para qué |
|---|---|---|
| `GET` | `/health` | Sonda de vida. No llama a servicios externos |
| `GET` | `/api/paises` | Países soportados con su moneda y tarifa |
| `GET` | `/api/ubicacion` | Coordenadas → ciudad y código de país |
| `POST` | `/api/analisis-energetico` (alias: `/analisis-energetico`) | Análisis del hogar. **El endpoint principal** |
| `GET` | `/api/analisis-energetico` (alias: `/analisis-energetico`) | Historial — últimos análisis (`?limite=`, Fase D) |
| `GET` | `/api/analisis-energetico/{id}` (alias sin `/api/`) | Consulta un análisis guardado por id (Fase D) |
| `POST` | `/api/calcular` | Cálculo por artefacto. Payload **distinto** al anterior |
| `POST` | `/api/subir-boleta` | Extrae consumo y tarifa de una boleta |
| `POST` | `/api/interpretar-campo` | Mapea texto libre a un tipo de vivienda |
| `POST` | `/api/comparar` | Compara artefactos. Catálogo de ejemplo |

El alias sin `/api/` existe porque las bases del hackathon especifican la ruta exacta
`POST /analisis-energetico` (Fase C / decisión H-2) — mismo código, misma cuota de límite de tasa,
ambas rutas apuntan al mismo view function.

Los endpoints que consumen servicios de pago tienen límite de tasa por IP y no piden credenciales;
sin tope, cualquiera podría agotar la cuota.

---

## Desarrollo

### Ejecutar la batería de pruebas

**Con un entorno local** (rápido, para iterar):

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

> El `venv/` que hay en el repositorio es de Windows y no sirve en macOS ni Linux. De ahí que el
> entorno nuevo se llame `.venv`, con punto: son directorios distintos y ambos están ignorados por git.

**Dentro de un contenedor** (misma versión de Python que la CI, sin instalar nada):

```bash
docker run --rm -v "$PWD:/app" -w /app python:3.12-slim \
  sh -c "pip install -q -r requirements-dev.txt && pytest"
```

Úsalo si tu Python local no es 3.12: la batería pasa igual en 3.9, pero solo esta vía reproduce
exactamente lo que corre en la CI.

Algunos tests solo corren con `ENABLE_API_DOCS=1` —los de la interfaz visual de la API— y se saltan
en caso contrario. Ninguno llama a Groq ni a OpenStreetMap: la batería funciona sin claves y sin red.

La CI ejecuta linter y tests en cada PR, construye la imagen de Docker, la arranca y sondea
`/health`, y falla si alguien versiona un `.env` o un `.zip`.

### Datos de referencia

[`data/consumo_referencia.json`](data/consumo_referencia.json) es la fuente única de potencias,
tarifas y suposiciones de uso. Cada valor lleva anotada su procedencia, y los que no están
verificados lo dicen explícitamente:

- **Tarifas por país:** referenciales, con el regulador de origen anotado. No están verificadas en
  tiempo real — envía `tarifa_kwh` con el valor de tu propia boleta para obtener importes exactos.
- **`perfil_hogar`:** las horas de uso al día y las veces por semana de cada equipo. Antes eran
  constantes escondidas en el código; ahora se pueden auditar y corregir aquí.
- **Marcados `SIN VERIFICAR`:** la potencia media de la lavadora y las tarifas de siete países.
  Sustituirlos por datos reales antes de presentar esto como asesoría.
- **`categorias_comparables`:** catálogo **de ejemplo**, con todos los precios en `null`.

---

## Estructura

```
desafioTeam49/
├── app.py                      Servidor Flask y endpoints
├── src/
│   ├── calculos.py             Motor determinista
│   ├── modelo.py                Carga del modelo entrenado (Fase A/B)
│   ├── oci_storage.py           Sincronización con OCI Object Storage (Fase E)
│   ├── almacen.py               Historial de análisis, SQLite (Fase D)
│   ├── llm.py                  Acceso a Groq
│   └── geo.py                  Geocodificación inversa
├── scripts/generar_dataset.py  Genera data/consumo_hogares.csv (semilla fija)
├── notebooks/energiai.ipynb    EDA, entrenamiento, evaluación, serialización
├── modelos/
│   ├── clasificador_energetico.joblib
│   └── metadatos.json          Versión de sklearn, métricas, orden de features
├── data/
│   ├── consumo_referencia.json
│   └── consumo_hogares.csv     Dataset sintético (Fase A.1)
├── instance/analisis.db        Historial SQLite (no versionado, ver .gitignore)
├── templates/index.html
├── static/
│   ├── css/style.css
│   ├── js/app.js               Lógica del asistente
│   ├── js/denji.js             Asistente guiado
│   ├── img/
│   └── vendor/                 Lucide y la tipografía, servidos localmente
├── tests/                      Batería de pruebas
├── docs/
│   ├── EnergiAI.pdf            Bases del hackathon (la fuente)
│   ├── EJEMPLOS.md              Tres casos de uso reales, contra el servidor (Fase F)
│   ├── openapi.yaml            Contrato de la API
│   ├── reglas_recomendaciones.md  Tabla de datacience detrás de las recomendaciones
│   ├── PLAN.md                 Plan de la auditoría de código
│   ├── PLAN-HACKATHON.md       Qué falta para cumplir las bases
│   └── DECISIONES.md           Decisiones técnicas y su porqué
├── Dockerfile                  Multi-stage, sin privilegios
├── docker-compose.yml
├── requirements.txt            Dependencias directas
├── requirements.lock           Árbol completo fijado (build reproducible)
└── requirements-dev.txt
```

---

## Comandos

Referencia de lo que se usa a diario. Los de Docker asumen que estás en la raíz del proyecto.

### Levantar y parar

```bash
docker compose up -d                 # arrancar en segundo plano
docker compose up                    # arrancar viendo los logs
docker compose down                  # parar y eliminar el contenedor
docker compose restart               # reiniciar sin recrear
docker compose ps                    # ¿está viva? ¿en qué puerto?
docker compose logs -f               # seguir los logs en vivo
docker compose logs --tail 50 app    # las últimas 50 líneas
```

### Cuándo hace falta reconstruir

Editar `app.py`, `src/`, `static/` o `templates/` **no requiere nada**: el código va montado y
gunicorn recarga solo. El resto sí:

| Cambiaste… | Comando |
|---|---|
| El `.env` | `docker compose up -d --force-recreate` |
| `requirements.lock` o el `Dockerfile` | `docker compose up -d --build` |
| Quieres Swagger UI en la imagen | `INSTALAR_DOCS=1 docker compose build && docker compose up -d` |

El entorno se lee al **crear** el contenedor, no en cada petición: por eso un cambio en el `.env`
necesita `--force-recreate` y no basta con `restart`.

### Pruebas y linter

```bash
source .venv/bin/activate            # una vez por terminal

pytest                               # toda la batería
pytest tests/test_calculos.py        # un solo archivo
pytest tests/test_calculos.py::test_hervidor_coincide_con_la_termodinamica   # un solo test
pytest -k tarifa                     # los que coincidan con un nombre
pytest -x                            # parar en el primer fallo
pytest -q --cov=src --cov=app --cov-report=term          # con cobertura
pytest -q --cov=src --cov-report=html && open htmlcov/index.html   # cobertura navegable

ruff check .                         # linter
ruff check . --fix                   # y que corrija lo que pueda
```

### Comprobar que funciona

```bash
curl -s localhost:5001/health | python3 -m json.tool     # estado y qué hay configurado
curl -s localhost:5001/api/paises | python3 -m json.tool # catálogo de países

curl -s -X POST localhost:5001/api/analisis-energetico \
  -H 'Content-Type: application/json' \
  -d '{"pais":"CL","tv":2,"tv_frecuencia":21,"refrigerador":1}' | python3 -m json.tool
```

`/health` dice de un vistazo si las funciones opcionales están activas:

```json
{"estado":"ok","paises":24,"artefactos":31,
 "groq_configurado":true,"geocodificacion_configurada":true}
```

### Diagnosticar problemas

```bash
docker compose logs app | grep -i "GROQ_API_KEY rechazada"   # ¿la clave caducó?
docker compose logs app | grep -iE "error|warning"           # todo lo anómalo
docker compose exec app sh                                   # entrar al contenedor
docker compose exec app printenv | grep -c GROQ              # ¿llegaron las variables?
```

En el navegador, para el asistente de voz —consola con `Cmd+Option+J`—:

```js
denjiDiagnostico()            // navegador, permisos del micrófono, idioma
denjiUltimaTranscripcion      // lo último que se reconoció
```

Y filtra por `[denji:voz]` para seguir cada fase de la escucha.

### Git

```bash
git status --short
git log --oneline -10
git diff                             # cambios sin preparar
git diff --cached                    # los que ya están preparados
```

---

## Tecnologías

| Capa | Stack |
|---|---|
| **Backend** | Python 3.12, Flask 3, gunicorn, flask-limiter |
| **Modelo de eficiencia** | scikit-learn (Regresión Logística, 97,3% exactitud) + joblib + pandas — entrenado en `notebooks/energiai.ipynb`, servido por `src/modelo.py` |
| **Narrativa y lectura de boletas** | LangChain + Groq (Llama 3.3 70B; visión con Llama 4 Scout) — nunca calcula, solo redacta |
| **Asistente guiado** | Denji (`static/js/denji.js`) — voz, mic, y sincronización bidireccional con el formulario |
| **Geocodificación** | Nominatim/OpenStreetMap, vía `src/geo.py` (identificado, con caché y límite de tasa) |
| **Persistencia** | SQLite (`src/almacen.py`) — historial de análisis, consultable por id |
| **Almacenamiento del modelo** | OCI Object Storage (`src/oci_storage.py`) — Instance Principal, con degradación a modelo local |
| **Frontend** | HTML5, CSS3, JavaScript ES6+ — sin framework ni CDN |
| **Datos** | JSON de referencia + dataset sintético (`data/consumo_hogares.csv`), cálculo determinista |
| **Infra** | Docker multi-stage, GitHub Actions (lint + tests + build de imagen) |

La interfaz **no hace ninguna petición a servidores externos** salvo las que requieren un servicio
específico (geocodificación, el LLM, o descargar el modelo desde OCI la primera vez) — los iconos y
la tipografía se sirven desde el propio proyecto, y cada una de esas integraciones se degrada
explícitamente si no está disponible, sin tumbar la app.

---

VólticvS © 2026 — Equipo Volti
