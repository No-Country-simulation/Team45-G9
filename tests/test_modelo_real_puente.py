"""
Tests de src/modelo_real_puente.py — la traducción entre nuestro payload
(el que llena el wizard) y el `obs` que espera el modelo real de datacience.
"""
from src import modelo_real_puente as puente


def _d_base(**overrides) -> dict:
    base = {
        "pais": "CL", "estado_provincia": "Santiago", "dormitorios": 2, "ventanas": 5,
        "habitantes_mayores": 2, "habitantes_menores": 0, "aire_acondicionado": 0,
        "calefaccion_electrica": 0, "agua_caliente_electrica": 1, "secarropas_electrico": 0,
        "horno_electrico": 0, "refrigerador": 1, "freezer": 0, "tv": 1, "tv_frecuencia": 10,
        "lavado_frecuencia": 2, "luces_exterior": 1, "luces_interior": 2,
    }
    base.update(overrides)
    return base


class TestPaisesSoportados:
    def test_chile_calcula_resultado_real(self):
        resultado = puente.calcular(_d_base(pais="CL"), consumo_kwh=200)
        assert resultado is not None
        assert "Indice de eficiencia" in resultado["salida"]

    def test_usa_calcula_resultado_real(self):
        resultado = puente.calcular(_d_base(pais="US", estado_provincia="California"), consumo_kwh=200)
        assert resultado is not None

    def test_pais_no_soportado_devuelve_none_sin_lanzar(self):
        """España no está entre los 35 países del modelo real."""
        assert puente.calcular(_d_base(pais="ES", estado_provincia="Madrid"), consumo_kwh=200) is None

    def test_pais_vacio_devuelve_none(self):
        assert puente.calcular(_d_base(pais=""), consumo_kwh=200) is None


class TestMapeoDeCampos:
    def test_tv_se_traduce_a_tv_cantidad(self):
        obs = puente._construir_obs(_d_base(tv=3), consumo_kwh=200)
        assert obs["tv_cantidad"] == 3

    def test_lavado_frecuencia_se_traduce_a_lavarropas_frecuencia(self):
        obs = puente._construir_obs(_d_base(lavado_frecuencia=5), consumo_kwh=200)
        assert obs["lavarropas_frecuencia"] == 5

    def test_luces_interior_se_traduce_a_luces_interior_4_horas(self):
        obs = puente._construir_obs(_d_base(luces_interior=7), consumo_kwh=200)
        assert obs["luces_interior_4_horas"] == 7

    def test_consumo_siempre_se_manda_como_mensual(self):
        obs = puente._construir_obs(_d_base(), consumo_kwh=200)
        assert obs["periodo_anual"] == 0
        assert obs["kwh"] == 200


class TestMapeoDeEstadoProvincia:
    def test_provincia_reconocida_usa_su_codigo_real(self):
        obs = puente._construir_obs(_d_base(pais="CL", estado_provincia="Valparaíso"), consumo_kwh=200)
        assert obs["estado"] == 14

    def test_provincia_no_reconocida_cae_al_estado_por_defecto(self):
        obs = puente._construir_obs(_d_base(pais="CL", estado_provincia="esto no existe"), consumo_kwh=200)
        assert obs["estado"] == puente.ESTADO_POR_DEFECTO["CL"]

    def test_provincia_vacia_cae_al_estado_por_defecto_usa(self):
        obs = puente._construir_obs(_d_base(pais="US", estado_provincia=""), consumo_kwh=200)
        assert obs["estado"] == puente.ESTADO_POR_DEFECTO["US"]
