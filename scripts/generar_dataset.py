"""
Generador del dataset sintético de hogares — Fase A.1 del plan de hackathon.

Por qué sintético y no un dataset público descargado: las bases del hackathon
(EnergiAI.pdf) permiten explícitamente "recolectada de fuentes públicas,
generada manualmente o simulada", y este proyecto tiene algo que un dataset
genérico no tiene: un motor físico real (calculos.estimar_desde_perfil) que
ya convierte un perfil de hogar en consumo eléctrico con física verificable,
no con una fórmula de caja negra. Muestreamos hogares plausibles y dejamos que
el motor calcule su consumo real — los datos quedan internamente coherentes
en vez de ser ruido aleatorio.

Semilla fija (SEED=42): correr este script dos veces produce el mismo CSV,
byte a byte — es el criterio de aceptación de la tarea A.1.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import numpy as np
import pandas as pd

from src import calculos

SEED = 42
N_HOGARES = 3000

TIPOS_INMUEBLE = ["Casa", "Departamento", "Casa pareada", "Casa móvil", "Otro"]
PAISES = [c for c in json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "consumo_referencia.json")))["paises"].keys() if not c.startswith("_")]


def generar_hogar(rng: np.random.Generator) -> dict:
    """Genera un perfil de hogar plausible (no cualquier combinación es igual
    de probable — un monoambiente casi nunca tiene 3 refrigeradores)."""
    dormitorios = int(rng.choice([0, 1, 2, 3, 4, 5], p=[0.05, 0.15, 0.30, 0.30, 0.15, 0.05]))
    habitantes_mayores = max(1, int(rng.poisson(1 + dormitorios * 0.6)))
    habitantes_menores = int(rng.poisson(max(0, dormitorios - 1) * 0.4))
    ventanas = max(1, int(rng.normal(loc=(dormitorios + 1) * 2, scale=2)))

    aire_acondicionado = int(rng.random() < 0.35)
    calefaccion_electrica = int(rng.random() < 0.30)
    agua_caliente_electrica = int(rng.random() < 0.40)
    secarropas_electrico = int(rng.random() < 0.25)
    horno_electrico = int(rng.random() < 0.45)

    refrigerador = 1 if rng.random() < 0.97 else 0
    freezer = int(rng.random() < 0.20)
    tv = int(rng.choice([0, 1, 2, 3, 4], p=[0.03, 0.35, 0.35, 0.20, 0.07]))
    tv_frecuencia = float(np.clip(rng.normal(loc=20, scale=10), 0, 90)) if tv > 0 else 0.0
    lavado_frecuencia = float(np.clip(rng.normal(loc=3, scale=1.5), 0, 10))

    pais = str(rng.choice(PAISES))
    tipo_inmueble = str(rng.choice(TIPOS_INMUEBLE, p=[0.55, 0.30, 0.08, 0.02, 0.05]))

    return {
        "pais": pais, "tipo_inmueble": tipo_inmueble,
        "dormitorios": dormitorios, "ventanas": ventanas,
        "habitantes_mayores": habitantes_mayores, "habitantes_menores": habitantes_menores,
        "aire_acondicionado": aire_acondicionado, "calefaccion_electrica": calefaccion_electrica,
        "agua_caliente_electrica": agua_caliente_electrica, "secarropas_electrico": secarropas_electrico,
        "horno_electrico": horno_electrico, "refrigerador": refrigerador, "freezer": freezer,
        "tv": tv, "tv_frecuencia": tv_frecuencia, "lavado_frecuencia": lavado_frecuencia,
    }


def generar_dataset(n: int = N_HOGARES, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    filas = []
    for _ in range(n):
        hogar = generar_hogar(rng)
        tarifa = calculos.tarifa_de(hogar["pais"])
        resultado = calculos.estimar_desde_perfil(hogar, tarifa)

        cantidad_equipos = sum([
            hogar["aire_acondicionado"], hogar["calefaccion_electrica"],
            hogar["agua_caliente_electrica"], hogar["secarropas_electrico"],
            hogar["horno_electrico"], hogar["refrigerador"], hogar["freezer"], hogar["tv"],
        ])
        uso_horario_pico = int(
            (hogar["aire_acondicionado"] or hogar["calefaccion_electrica"])
            and (hogar["habitantes_mayores"] + hogar["habitantes_menores"]) >= 2
        )
        horas_alto_consumo = round(
            hogar["aire_acondicionado"] * 4.4 + hogar["calefaccion_electrica"] * 3.3
            + hogar["agua_caliente_electrica"] * 4.0, 1
        )

        filas.append({
            **hogar,
            "cantidad_equipos": cantidad_equipos,
            "uso_horario_pico": uso_horario_pico,
            "horas_alto_consumo": horas_alto_consumo,
            "tarifa_kwh": tarifa,
            "consumo_kwh": resultado["consumo_kwh"],
        })

    return pd.DataFrame(filas)


if __name__ == "__main__":
    df = generar_dataset()
    ruta_salida = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "consumo_hogares.csv")
    df.to_csv(ruta_salida, index=False)
    print(f"Dataset generado: {len(df)} hogares -> {ruta_salida}")
    print(df["consumo_kwh"].describe())
