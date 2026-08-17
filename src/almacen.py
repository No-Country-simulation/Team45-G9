"""
Persistencia del historial de análisis (Fase D del plan de hackathon).

SQLite por defecto — sin servicio extra que desplegar, tal como recomienda el
plan. La ruta es configurable por entorno (ANALISIS_DB_PATH); en Docker vive
en el volumen nombrado `analisis_db` (ver docker-compose.yml), no en el
tmpfs de uploads/ que se borra en cada restart.

Mismo espíritu que src/llm.py y src/geo.py: si algo falla al guardar, la
API no se cae — el análisis ya se calculó y se le devuelve igual al usuario,
solo que sin id de consulta. Guardar el historial es un extra, no algo de lo
que dependa la respuesta principal.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone

RUTA_DB = os.getenv(
    "ANALISIS_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "instance", "analisis.db"),
)

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS analisis (
    id TEXT PRIMARY KEY,
    fecha TEXT NOT NULL,
    pais TEXT,
    categoria TEXT,
    payload_json TEXT NOT NULL,
    resultado_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_analisis_fecha ON analisis(fecha DESC);
"""


def _conectar() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(RUTA_DB), exist_ok=True)
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row
    conexion.executescript(_ESQUEMA)
    return conexion


def guardar(payload: dict, resultado: dict) -> str | None:
    """Guarda un análisis y devuelve su id, o None si falló (nunca lanza —
    persistir el historial no puede tumbar la respuesta principal)."""
    try:
        id_analisis = str(uuid.uuid4())
        with _conectar() as conexion:
            conexion.execute(
                "INSERT INTO analisis (id, fecha, pais, categoria, payload_json, resultado_json) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    id_analisis,
                    datetime.now(timezone.utc).isoformat(),
                    payload.get("pais"),
                    resultado.get("categoria"),
                    json.dumps(payload, ensure_ascii=False),
                    json.dumps(resultado, ensure_ascii=False),
                ),
            )
        return id_analisis
    except Exception:
        return None


def obtener(id_analisis: str) -> dict | None:
    try:
        with _conectar() as conexion:
            fila = conexion.execute(
                "SELECT * FROM analisis WHERE id = ?", (id_analisis,)
            ).fetchone()
        if fila is None:
            return None
        return {
            "id": fila["id"],
            "fecha": fila["fecha"],
            "pais": fila["pais"],
            "categoria": fila["categoria"],
            "payload": json.loads(fila["payload_json"]),
            "resultado": json.loads(fila["resultado_json"]),
        }
    except Exception:
        return None


def listar(limite: int = 20) -> list[dict]:
    """Los últimos `limite` análisis, más reciente primero. Sin el payload
    completo — para el listado alcanza con el resumen; el detalle completo
    está en obtener(id)."""
    try:
        limite = max(1, min(int(limite), 100))  # tope duro: nadie pide 10 millones de filas
        with _conectar() as conexion:
            filas = conexion.execute(
                "SELECT id, fecha, pais, categoria FROM analisis ORDER BY fecha DESC LIMIT ?",
                (limite,),
            ).fetchall()
        return [dict(f) for f in filas]
    except Exception:
        return []
