"""
Tests del checklist de bloques horarios (rangos_horario_uso) y la estadística
que genera — reemplaza el booleano ciego uso_horario_pico por un dato
auditable: qué bloques marcó el usuario, cuántas horas suman, y si alguno
cae en horario pico.
"""
import pytest

import app as aplicacion


@pytest.fixture(autouse=True)
def sin_llamadas_al_llm(monkeypatch):
    monkeypatch.setattr(
        aplicacion, "generar_narrativa", lambda resumen: {"texto": "narrativa de prueba", "fuente": "test"}
    )
    aplicacion.limiter.enabled = False


@pytest.fixture
def cliente():
    aplicacion.app.config["TESTING"] = True
    return aplicacion.app.test_client()


def analizar(cliente, **campos):
    respuesta = cliente.post("/api/analisis-energetico", json=campos)
    assert respuesta.status_code == 200, respuesta.get_data(as_text=True)
    return respuesta.get_json()


class TestEstadisticaHorarioUso:
    def test_sin_rangos_marcados_la_estadistica_queda_vacia(self, cliente):
        r = analizar(cliente, pais="CL", refrigerador=1)
        est = r["estadistica_horario_uso"]
        assert est["cantidad_rangos_marcados"] == 0
        assert est["horas_totales_declaradas"] == 0
        assert est["coincide_con_horario_pico"] is False

    def test_un_rango_fuera_de_pico_no_marca_coincidencia(self, cliente):
        r = analizar(cliente, pais="CL", refrigerador=1, rangos_horario_uso=["manana"])
        est = r["estadistica_horario_uso"]
        assert est["rangos_seleccionados"] == ["manana"]
        assert est["horas_totales_declaradas"] == 4  # 09:00-13:00
        assert est["coincide_con_horario_pico"] is False
        assert r["uso_horario_pico"] is False

    def test_noche_pico_marca_coincidencia_y_uso_horario_pico(self, cliente):
        r = analizar(cliente, pais="CL", refrigerador=1, rangos_horario_uso=["noche_pico"])
        est = r["estadistica_horario_uso"]
        assert est["coincide_con_horario_pico"] is True
        assert r["uso_horario_pico"] is True

    def test_varios_rangos_suman_horas_correctamente(self, cliente):
        r = analizar(
            cliente, pais="CL", refrigerador=1,
            rangos_horario_uso=["madrugada", "manana_temprano", "noche_pico"]
        )
        est = r["estadistica_horario_uso"]
        assert est["cantidad_rangos_marcados"] == 3
        assert est["horas_totales_declaradas"] == 6 + 3 + 4  # 0-6, 6-9, 18-22

    def test_rango_invalido_se_ignora_sin_reventar(self, cliente):
        r = analizar(cliente, pais="CL", refrigerador=1, rangos_horario_uso=["noche_pico", "inventado_no_existe"])
        est = r["estadistica_horario_uso"]
        assert est["rangos_seleccionados"] == ["noche_pico"]
        assert est["cantidad_rangos_marcados"] == 1

    def test_rangos_marcados_tienen_prioridad_sobre_la_heuristica_de_artefactos(self, cliente):
        """Un hogar con aire acondicionado y 2 habitantes activaría la
        heurística vieja (True), pero si el usuario declaró explícitamente
        que NO usa electricidad en horario pico (ningún rango de noche),
        el dato real que dio la persona debe ganar."""
        r = analizar(
            cliente, pais="CL", refrigerador=1, aire_acondicionado=1, habitantes_mayores=2,
            rangos_horario_uso=["manana_temprano"]
        )
        assert r["uso_horario_pico"] is False

    def test_rangos_disponibles_documenta_las_7_opciones(self, cliente):
        r = analizar(cliente, pais="CL", refrigerador=1)
        assert len(r["estadistica_horario_uso"]["rangos_disponibles"]) == 7
