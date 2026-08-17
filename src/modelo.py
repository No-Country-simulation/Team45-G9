"""
Carga del modelo de clasificación entrenado (Fase B.1 del plan de hackathon).

Mismo patrón que `src/llm.py` y `src/geo.py`: carga perezosa y cacheada, con
degradación explícita si el recurso no está disponible — acá, si
`modelos/clasificador_energetico.joblib` no existe (por ejemplo, en un clon
que no corrió el notebook, o antes de que Fase E lo descargue de OCI), la API
sigue funcionando con los umbrales fijos anteriores en vez de caerse, y lo
declara en la respuesta (`fuente_clasificacion`) en vez de fingir que vino
del modelo.

El notebook (`notebooks/energiai.ipynb`) es la fuente de verdad de cómo se
entrenó; este módulo solo lo carga y lo sirve.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache

from src import oci_storage

RUTA_MODELO = os.getenv(
    "MODELO_CLASIFICADOR_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modelos", "clasificador_energetico.joblib"),
)
RUTA_METADATOS = os.path.join(os.path.dirname(RUTA_MODELO), "metadatos.json")

# Umbrales fijos de respaldo — los que ya existían antes del modelo entrenado.
UMBRAL_EFICIENTE = 250
UMBRAL_MODERADO = 450

_estado_sincronizacion_oci: dict = {}


@lru_cache(maxsize=1)
def _cargar_modelo():
    """Devuelve (pipeline_sklearn, metadatos) o (None, None) si no existe el
    archivo, ni siquiera después de intentar traerlo de OCI. Cacheado: la
    sincronización con OCI y el joblib.load solo se pagan una vez por
    proceso."""
    global _estado_sincronizacion_oci
    _estado_sincronizacion_oci = oci_storage.sincronizar_modelo(RUTA_MODELO, RUTA_METADATOS)

    if not os.path.exists(RUTA_MODELO):
        return None, None
    import joblib
    modelo = joblib.load(RUTA_MODELO)
    metadatos = {}
    if os.path.exists(RUTA_METADATOS):
        with open(RUTA_METADATOS, encoding="utf-8") as f:
            metadatos = json.load(f)
    return modelo, metadatos


def estado_oci() -> dict:
    """Para /health — de dónde salió (o no) el modelo cargado."""
    _cargar_modelo()  # asegura que ya se intentó sincronizar al menos una vez
    return dict(_estado_sincronizacion_oci)


def modelo_disponible() -> bool:
    modelo, _ = _cargar_modelo()
    return modelo is not None


def clasificar(datos_hogar: dict, consumo_kwh: float, fuente_consumo: str = "estimado") -> dict:
    """Clasifica un hogar en Eficiente/Moderado/Ineficiente.

    - Si el modelo está disponible Y el consumo viene ESTIMADO del perfil de
      artefactos (con lo que el modelo se entrenó): usa predict()/predict_proba().
    - Si el consumo es DECLARADO (boleta/manual): las variables por artefacto
      pueden no reflejar ese número, así que usar el modelo ahí daría una
      predicción inconsistente. Se cae a los umbrales fijos sobre el kWh
      declarado, con probabilidad None (no se inventa una).
    - Si el modelo no está disponible: mismo respaldo por umbrales.
    """
    modelo, metadatos = _cargar_modelo()

    if modelo is not None and fuente_consumo == "estimado":
        orden_features = metadatos.get("orden_features_entrada", [])
        fila = {campo: datos_hogar.get(campo, 0) for campo in orden_features}
        import pandas as pd
        X = pd.DataFrame([fila])
        categoria = modelo.predict(X)[0]
        clases = list(modelo.classes_)
        probabilidades = modelo.predict_proba(X)[0]
        probabilidad = float(probabilidades[clases.index(categoria)])
        return {"categoria": categoria, "probabilidad": round(probabilidad, 4), "fuente_clasificacion": "modelo"}

    if consumo_kwh < UMBRAL_EFICIENTE:
        categoria = "Eficiente"
    elif consumo_kwh < UMBRAL_MODERADO:
        categoria = "Moderado"
    else:
        categoria = "Ineficiente"
    return {"categoria": categoria, "probabilidad": None, "fuente_clasificacion": "umbrales"}
