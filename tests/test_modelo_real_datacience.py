"""
Tests del modelo real de datacience (src/modelo_real_datacience.py).

El test más importante de este archivo (TestFidelidadContraElOriginal) corre
el script ORIGINAL de datacience de verdad —tal cual lo entregaron, sin
tocar una línea— y compara su OUTPUT.json contra lo que devuelve nuestra
función envuelta, para el mismo INPUT.json. Si alguna vez alguien modifica
por error una línea del envoltorio, este test lo detecta comparando contra
la fuente real, no contra un valor fijo escrito a mano.

docs/referencia/Modelo_original_datacience.py es una copia intacta del
script que entregó datacience — nunca se importa ni se usa en producción,
solo aquí, para esta comparación.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.modelo_real_datacience import predecir_eficiencia_real

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT_ORIGINAL = RAIZ / "docs" / "referencia" / "Modelo_original_datacience.py"


def _correr_script_original(obs: dict, tmp_path: Path) -> dict:
    """Corre el script original de verdad, en una carpeta temporal (para no
    ensuciar el repo con INPUT.json/OUTPUT.json sueltos), y devuelve su
    resultado real."""
    (tmp_path / "INPUT.json").write_text(json.dumps(obs), encoding="utf-8")
    subprocess.run(
        [sys.executable, str(SCRIPT_ORIGINAL)],
        cwd=tmp_path, check=True, capture_output=True, timeout=30,
    )
    return json.loads((tmp_path / "OUTPUT.json").read_text(encoding="utf-8"))


def _obs_base(**overrides) -> dict:
    base = {
        "pais": 27, "estado": 22, "dormitorios": 3, "ventanas": 8,
        "habitantes_mayores": 2, "habitantes_menores": 1, "aire_acondicionado": 1,
        "calefaccion_electrica": 0, "agua_caliente_electrica": 1,
        "agua_caliente_tamano": 0, "flag_galones": 0, "secarropas_electrico": 0,
        "horno_electrico": 1, "refrigerador": 1, "freezer": 0, "tv_cantidad": 2,
        "tv_frecuencia": 14, "lavarropas_frecuencia": 3, "luces_exterior": 3,
        "luces_interior_4_horas": 4, "kwh": 250, "periodo_anual": 0,
    }
    base.update(overrides)
    return base


@pytest.mark.skipif(not SCRIPT_ORIGINAL.exists(), reason="No está la copia de referencia del script original")
class TestFidelidadContraElOriginal:
    """Cada caso corre el script real de datacience Y la función envuelta,
    con el mismo input, y exige que el resultado sea IDÉNTICO — no
    aproximado, idéntico byte a byte del JSON."""

    def test_chile_hogar_grande_ineficiente(self, tmp_path):
        obs = _obs_base(dormitorios=5, ventanas=16, habitantes_mayores=4, habitantes_menores=2,
                         aire_acondicionado=1, calefaccion_electrica=1, secarropas_electrico=1,
                         freezer=1, tv_cantidad=3, tv_frecuencia=28, lavarropas_frecuencia=5,
                         luces_exterior=6, luces_interior_4_horas=8, kwh=800)
        assert predecir_eficiencia_real(dict(obs)) == _correr_script_original(obs, tmp_path)

    def test_usa_california_hogar_chico(self, tmp_path):
        obs = _obs_base(pais=2, estado=5, dormitorios=1, ventanas=2, habitantes_mayores=1,
                         habitantes_menores=0, aire_acondicionado=0, agua_caliente_electrica=0,
                         horno_electrico=0, tv_cantidad=1, tv_frecuencia=5, lavarropas_frecuencia=1,
                         luces_exterior=0, luces_interior_4_horas=1, kwh=60)
        assert predecir_eficiencia_real(dict(obs)) == _correr_script_original(obs, tmp_path)

    def test_canada_usa_modelo_prestado_de_usa(self, tmp_path):
        obs = _obs_base(pais=1, estado=1, dormitorios=2, ventanas=6, habitantes_mayores=2,
                         habitantes_menores=1, aire_acondicionado=0, calefaccion_electrica=1,
                         secarropas_electrico=1, horno_electrico=0, tv_cantidad=2, tv_frecuencia=10,
                         lavarropas_frecuencia=3, luces_exterior=2, luces_interior_4_horas=3, kwh=300)
        assert predecir_eficiencia_real(dict(obs)) == _correr_script_original(obs, tmp_path)

    def test_argentina_usa_modelo_prestado_de_chile(self, tmp_path):
        obs = _obs_base(pais=24, estado=1, dormitorios=3, ventanas=7, habitantes_mayores=3,
                         habitantes_menores=0, tv_cantidad=2, tv_frecuencia=15,
                         lavarropas_frecuencia=4, luces_exterior=2, luces_interior_4_horas=3, kwh=280)
        assert predecir_eficiencia_real(dict(obs)) == _correr_script_original(obs, tmp_path)

    def test_consumo_declarado_en_periodo_anual(self, tmp_path):
        obs = _obs_base(estado=40, dormitorios=2, ventanas=5, habitantes_mayores=2,
                         habitantes_menores=0, aire_acondicionado=0, horno_electrico=0,
                         tv_cantidad=1, tv_frecuencia=12, lavarropas_frecuencia=2,
                         luces_exterior=1, luces_interior_4_horas=2, kwh=2400, periodo_anual=1)
        assert predecir_eficiencia_real(dict(obs)) == _correr_script_original(obs, tmp_path)

    def test_hogar_extremadamente_eficiente(self, tmp_path):
        obs = _obs_base(dormitorios=0, ventanas=1, habitantes_mayores=1, habitantes_menores=0,
                         aire_acondicionado=0, agua_caliente_electrica=0, horno_electrico=0,
                         tv_cantidad=0, tv_frecuencia=0, lavarropas_frecuencia=0,
                         luces_exterior=0, luces_interior_4_horas=0, kwh=15)
        assert predecir_eficiencia_real(dict(obs)) == _correr_script_original(obs, tmp_path)


class TestFormaDelResultado:
    """Sin depender del script original — solo confirma que la forma del
    resultado es la esperada, para detectar si algo cambia de estructura."""

    def test_tiene_las_tres_secciones_principales(self):
        r = predecir_eficiencia_real(_obs_base())
        assert set(r.keys()) == {"salida", "salida_complementaria", "estimacion_financiera"}

    def test_salida_tiene_el_indice_y_la_letra_de_eficiencia(self):
        r = predecir_eficiencia_real(_obs_base())
        assert -100 <= r["salida"]["Indice de eficiencia"] <= 100
        assert r["salida"]["Perfil de eficiencia"] in ("G", "F", "E", "D", "C", "B", "A", "A+", "A++")

    def test_recomendaciones_son_texto_real_no_vacio(self):
        r = predecir_eficiencia_real(_obs_base())
        recomendaciones = r["salida_complementaria"]["recomendaciones"]
        assert isinstance(recomendaciones, list)
        assert len(recomendaciones) > 0
        assert all(isinstance(rec, str) and len(rec) > 10 for rec in recomendaciones)
