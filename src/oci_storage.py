"""
Integración con OCI Object Storage (Fase E del plan de hackathon).

Descarga el modelo entrenado (`modelos/clasificador_energetico.joblib` +
`metadatos.json`) desde un bucket de Object Storage al arrancar, si no
existen ya en local. Mismo espíritu que `src/geo.py` con Nominatim:
degradación explícita, nunca un error que tumbe la app.

Autenticación, en este orden:
1. **Instance Principal** — sin ninguna clave que gestionar. Funciona solo
   cuando el proceso corre DENTRO de una VM de OCI Compute con un dynamic
   group + policy que le den permiso de lectura sobre el bucket (eso es
   infraestructura, no código — lo configura quien administre la cuenta de
   OCI, no este módulo). Como la API ya se aloja en OCI Compute, esta es la
   vía esperada en producción.
2. **Config file** (`~/.oci/config`, perfil `DEFAULT` o `OCI_CONFIG_PROFILE`)
   — para desarrollo local, en una máquina que no es una VM de OCI.
3. **Sin credenciales disponibles** — se degrada: usa lo que ya haya en
   `modelos/` localmente (el notebook lo deja ahí al entrenar), o los
   umbrales fijos si tampoco hay nada local. La app sigue funcionando en
   cualquiera de los dos casos.

Variables de entorno:
    OCI_BUCKET_NAMESPACE   — namespace del tenancy (obligatoria para activar esto)
    OCI_BUCKET_NAME        — nombre del bucket (obligatoria para activar esto)
    OCI_MODEL_OBJECT       — nombre del objeto del modelo (default: clasificador_energetico.joblib)
    OCI_METADATOS_OBJECT   — nombre del objeto de metadatos (default: metadatos.json)
    OCI_CONFIG_PROFILE     — perfil de ~/.oci/config a usar en modo config-file (default: DEFAULT)
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger("volticvs.oci")

OCI_BUCKET_NAMESPACE = os.getenv("OCI_BUCKET_NAMESPACE")
OCI_BUCKET_NAME = os.getenv("OCI_BUCKET_NAME")
OCI_MODEL_OBJECT = os.getenv("OCI_MODEL_OBJECT", "clasificador_energetico.joblib")
OCI_METADATOS_OBJECT = os.getenv("OCI_METADATOS_OBJECT", "metadatos.json")
OCI_CONFIG_PROFILE = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")


def oci_configurado() -> bool:
    """OCI_BUCKET_NAMESPACE y OCI_BUCKET_NAME son las únicas obligatorias —
    sin ellas no hay bucket que consultar, sin importar qué credenciales haya."""
    return bool(OCI_BUCKET_NAMESPACE and OCI_BUCKET_NAME)


def _obtener_cliente():
    """Intenta Instance Principal primero, config-file después. Devuelve
    None (no lanza) si ninguno de los dos funciona — quien llame decide
    cómo degradar."""
    try:
        import oci
    except ImportError:
        logger.warning("oci_storage: el paquete 'oci' no está instalado — pip install oci")
        return None

    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        cliente = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
        logger.info("oci_storage: autenticado con Instance Principal")
        return cliente
    except Exception as e:
        logger.info(f"oci_storage: Instance Principal no disponible ({type(e).__name__}), probando config-file")

    try:
        config = oci.config.from_file(profile_name=OCI_CONFIG_PROFILE)
        cliente = oci.object_storage.ObjectStorageClient(config)
        logger.info(f"oci_storage: autenticado con config-file (perfil {OCI_CONFIG_PROFILE})")
        return cliente
    except Exception as e:
        logger.warning(f"oci_storage: sin credenciales disponibles ({type(e).__name__}) — se usa el modelo local")
        return None


def _descargar_objeto(cliente, nombre_objeto: str, ruta_destino: str) -> bool:
    try:
        respuesta = cliente.get_object(OCI_BUCKET_NAMESPACE, OCI_BUCKET_NAME, nombre_objeto)
        os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
        with open(ruta_destino, "wb") as f:
            for parte in respuesta.data.raw.stream(1024 * 1024, decode_content=False):
                f.write(parte)
        logger.info(f"oci_storage: descargado {nombre_objeto} -> {ruta_destino}")
        return True
    except Exception as e:
        logger.warning(f"oci_storage: no se pudo descargar {nombre_objeto}: {type(e).__name__}: {e}")
        return False


def sincronizar_modelo(ruta_modelo: str, ruta_metadatos: str, forzar: bool = False) -> dict:
    """Descarga el modelo desde OCI si:
      - OCI está configurado (namespace + bucket), Y
      - el archivo local no existe todavía (o forzar=True).

    Si el archivo local YA existe y no se fuerza, no se toca — evita
    descargar en cada arranque cuando ya está ahí (el notebook, por ejemplo,
    lo deja localmente al entrenar).

    Devuelve un dict de estado para /health — nunca lanza.
    """
    estado = {
        "oci_configurado": oci_configurado(),
        "modelo_local_ya_existia": os.path.exists(ruta_modelo),
        "descargado_de_oci": False,
    }

    if not oci_configurado():
        return estado

    if estado["modelo_local_ya_existia"] and not forzar:
        return estado

    cliente = _obtener_cliente()
    if cliente is None:
        return estado

    ok_modelo = _descargar_objeto(cliente, OCI_MODEL_OBJECT, ruta_modelo)
    _descargar_objeto(cliente, OCI_METADATOS_OBJECT, ruta_metadatos)  # best-effort, no bloquea si falla
    estado["descargado_de_oci"] = ok_modelo
    return estado
