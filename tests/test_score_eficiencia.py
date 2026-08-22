"""
Tests del score de eficiencia (-100 a +100), la letra (G a A++), y la
interpretación (Muy baja a Muy alta) — directriz del líder técnico.

Estos tests usan pais="ES" (España) a propósito: es un país que NO está
entre los 35 que soporta el modelo real de datacience, así que fuerzan el
camino de respaldo (percentil contra nuestro dataset sintético) sin
depender de si el modelo real está disponible o no en este entorno. Los
tests del modelo real viven en tests/test_modelo_real_datacience.py.
"""
import json

import pytest

from src import modelo

D_PAIS_SIN_MODELO_REAL = {"pais": "ES"}


class TestCalculoDelScore:
    def test_hogar_de_muy_bajo_consumo_da_score_alto_positivo(self):
        r = modelo.calcular_score_eficiencia(D_PAIS_SIN_MODELO_REAL, 41)  # el mínimo del dataset
        assert r["score"] > 80

    def test_hogar_de_muy_alto_consumo_da_score_negativo(self):
        r = modelo.calcular_score_eficiencia(D_PAIS_SIN_MODELO_REAL, 809)  # el máximo del dataset
        assert r["score"] < -80

    def test_hogar_en_la_mediana_da_score_cercano_a_cero(self):
        r = modelo.calcular_score_eficiencia(D_PAIS_SIN_MODELO_REAL, 344)  # mediana aproximada del dataset
        assert -10 <= r["score"] <= 10

    def test_el_score_nunca_se_sale_de_menos_100_a_100(self):
        for consumo in [0, 1, 41, 344, 809, 5000, 999999]:
            r = modelo.calcular_score_eficiencia(D_PAIS_SIN_MODELO_REAL, consumo)
            assert -100 <= r["score"] <= 100

    def test_el_score_es_float_nativo_no_numpy(self):
        """Bug real encontrado antes de subir: np.float64 no siempre
        serializa bien con jsonify de Flask — tiene que ser float nativo."""
        r = modelo.calcular_score_eficiencia(D_PAIS_SIN_MODELO_REAL, 200)
        assert type(r["score"]) is float
        json.dumps(r)  # no debe lanzar

    def test_fuente_es_percentil_para_pais_sin_modelo_real(self):
        r = modelo.calcular_score_eficiencia(D_PAIS_SIN_MODELO_REAL, 200)
        assert r["fuente"] == "percentil_sintetico"


class TestLetraEIntepretacion:
    @pytest.mark.parametrize("score,letra_esperada", [
        (-100, "G"), (-90, "G"), (-80, "F"), (-70, "F"), (-60, "E"),
        (-50, "E"), (-40, "D"), (-30, "D"), (-20, "C"), (0, "C"), (19, "C"),
        (20, "B"), (39, "B"), (40, "A"), (59, "A"), (60, "A+"), (79, "A+"),
        (80, "A++"), (100, "A++"),
    ])
    def test_letra_segun_rango_confirmado(self, score, letra_esperada):
        assert modelo._mapear_rango(score, modelo.RANGOS_LETRA) == letra_esperada

    @pytest.mark.parametrize("score,interpretacion_esperada", [
        (-100, "Muy baja"), (-70, "Muy baja"), (-60, "Baja"), (-30, "Baja"),
        (-20, "Moderada"), (0, "Moderada"), (19, "Moderada"),
        (20, "Alta"), (59, "Alta"), (60, "Muy alta"), (100, "Muy alta"),
    ])
    def test_interpretacion_segun_rango_confirmado(self, score, interpretacion_esperada):
        assert modelo._mapear_rango(score, modelo.RANGOS_INTERPRETACION) == interpretacion_esperada


class TestDegradacionSinDataset:
    def test_sin_dataset_devuelve_none_en_vez_de_inventar(self, monkeypatch, tmp_path):
        monkeypatch.setattr(modelo, "RUTA_DATASET_ENTRENAMIENTO", str(tmp_path / "no_existe.csv"))
        modelo._cargar_distribucion_consumo.cache_clear()
        r = modelo.calcular_score_eficiencia(D_PAIS_SIN_MODELO_REAL, 200)
        assert r == {
            "score": None, "letra": None, "interpretacion": None, "fuente": "sin_datos",
            "ranking": None, "perfil_consumo": None, "recomendaciones_reales": [],
        }
        modelo._cargar_distribucion_consumo.cache_clear()  # no contaminar otros tests
