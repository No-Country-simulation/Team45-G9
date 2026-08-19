"""
Tests de la validación de rangos y advertencias del modelo entrenado
(punto 5 del feedback de datacience): valores fuera de rango se reemplazan
por la mediana real del dataset de entrenamiento, y se devuelve el aviso —
nunca se lanza una excepción por un dato raro.
"""
import pytest

from src import modelo


def _hogar_valido(**overrides):
    base = {
        "pais": "CL", "tipo_inmueble": "Casa",
        "dormitorios": 2, "ventanas": 5, "habitantes_mayores": 2, "habitantes_menores": 0,
        "aire_acondicionado": 0, "calefaccion_electrica": 0, "agua_caliente_electrica": 0,
        "secarropas_electrico": 0, "horno_electrico": 0, "refrigerador": 1, "freezer": 0,
        "tv": 1, "tv_frecuencia": 14, "lavado_frecuencia": 2,
        "cantidad_equipos": 2, "uso_horario_pico": 0, "horas_alto_consumo": 2,
    }
    base.update(overrides)
    return base


@pytest.fixture(autouse=True)
def modelo_de_verdad_disponible():
    """Estos tests necesitan el modelo entrenado real (modelos/*.joblib) —
    si no está disponible en este entorno, se saltan en vez de fallar."""
    if not modelo.modelo_disponible():
        pytest.skip("modelo entrenado no disponible en este entorno")


class TestValoresValidosNoGeneranAdvertencias:
    def test_hogar_con_valores_normales_no_tiene_advertencias(self):
        r = modelo.clasificar(_hogar_valido(), consumo_kwh=200, fuente_consumo="estimado")
        assert r["advertencias"] == []


class TestValoresFueraDeRangoGeneranAdvertenciaYSeCorrigen:
    def test_dormitorios_negativo_genera_advertencia(self):
        r = modelo.clasificar(_hogar_valido(dormitorios=-3), consumo_kwh=200, fuente_consumo="estimado")
        assert any("dormitorios" in a for a in r["advertencias"])
        assert r["categoria"] in ("Eficiente", "Moderado", "Ineficiente")  # no revienta

    def test_dormitorios_absurdamente_alto_genera_advertencia(self):
        r = modelo.clasificar(_hogar_valido(dormitorios=999), consumo_kwh=200, fuente_consumo="estimado")
        assert any("dormitorios" in a for a in r["advertencias"])

    def test_valor_no_numerico_genera_advertencia_y_no_revienta(self):
        r = modelo.clasificar(_hogar_valido(ventanas="muchas"), consumo_kwh=200, fuente_consumo="estimado")
        assert any("ventanas" in a for a in r["advertencias"])
        assert r["categoria"] in ("Eficiente", "Moderado", "Ineficiente")

    def test_multiples_campos_fuera_de_rango_generan_multiples_advertencias(self):
        r = modelo.clasificar(
            _hogar_valido(dormitorios=-1, tv_frecuencia=99999, habitantes_mayores=-5),
            consumo_kwh=200, fuente_consumo="estimado",
        )
        assert len(r["advertencias"]) >= 3

    def test_binario_fuera_de_0_1_genera_advertencia(self):
        r = modelo.clasificar(_hogar_valido(aire_acondicionado=5), consumo_kwh=200, fuente_consumo="estimado")
        assert any("aire_acondicionado" in a for a in r["advertencias"])


class TestConsumoDeclaradoNoValida:
    def test_consumo_declarado_no_ejecuta_validacion_del_modelo(self):
        """Si el consumo es declarado (boleta/manual), ni siquiera se llega a
        usar el modelo — cae a umbrales, sin advertencias del modelo posibles."""
        r = modelo.clasificar(_hogar_valido(dormitorios=-99), consumo_kwh=200, fuente_consumo="declarado")
        assert r["fuente_clasificacion"] == "umbrales"
        assert r["advertencias"] == []


class TestValidarYCompletarDirecto:
    def test_reemplaza_por_la_mediana_real_del_dataset(self):
        fila, advertencias = modelo._validar_y_completar({"dormitorios": -1})
        assert fila["dormitorios"] == modelo.RANGOS_VALIDOS["dormitorios"][2]
        assert len(advertencias) == 1

    def test_no_toca_campos_que_no_estan_en_rangos_validos(self):
        """pais y tipo_inmueble son categóricos (strings) — no deben pasar
        por esta validación numérica ni generar advertencias falsas."""
        fila, advertencias = modelo._validar_y_completar({"pais": "CL", "tipo_inmueble": "Casa"})
        assert fila == {"pais": "CL", "tipo_inmueble": "Casa"}
        assert advertencias == []
