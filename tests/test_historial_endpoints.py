"""
Tests de las rutas de consulta/listado del historial de análisis (Fase D),
a nivel HTTP — complementa tests/test_almacen.py (que prueba el módulo
directo, sin pasar por Flask).
"""
import pytest

import app as aplicacion


@pytest.fixture(autouse=True)
def entorno_de_prueba(tmp_path, monkeypatch):
    monkeypatch.setattr(
        aplicacion, "generar_narrativa", lambda resumen: {"texto": "narrativa de prueba", "fuente": "test"}
    )
    aplicacion.limiter.enabled = False
    # DB propia por test, para no compartir historial entre tests ni con el real.
    monkeypatch.setattr(aplicacion.almacen, "RUTA_DB", str(tmp_path / "historial_test.db"))


@pytest.fixture
def cliente():
    aplicacion.app.config["TESTING"] = True
    return aplicacion.app.test_client()


class TestPostGuardaYDevuelveId:
    def test_analisis_energetico_devuelve_un_id(self, cliente):
        r = cliente.post("/api/analisis-energetico", json={"pais": "CL", "refrigerador": 1})
        assert r.status_code == 200
        assert r.get_json()["id"] is not None

    def test_el_alias_tambien_guarda(self, cliente):
        r = cliente.post("/analisis-energetico", json={"pais": "CL", "refrigerador": 1})
        assert r.status_code == 200
        assert r.get_json()["id"] is not None


class TestGetConsultaPorId:
    def test_consultar_un_analisis_que_existe(self, cliente):
        creado = cliente.post("/api/analisis-energetico", json={"pais": "AR", "dormitorios": 2}).get_json()
        r = cliente.get(f"/api/analisis-energetico/{creado['id']}")
        assert r.status_code == 200
        registro = r.get_json()
        assert registro["id"] == creado["id"]
        assert registro["pais"] == "AR"
        assert registro["resultado"]["consumo_kwh"] == creado["consumo_kwh"]

    def test_consultar_un_id_inexistente_da_404(self, cliente):
        r = cliente.get("/api/analisis-energetico/id-que-no-existe")
        assert r.status_code == 404

    def test_el_alias_de_consulta_tambien_funciona(self, cliente):
        creado = cliente.post("/analisis-energetico", json={"pais": "CL"}).get_json()
        r = cliente.get(f"/analisis-energetico/{creado['id']}")
        assert r.status_code == 200


class TestGetListado:
    def test_listado_vacio_al_principio(self, cliente):
        r = cliente.get("/api/analisis-energetico")
        assert r.status_code == 200
        assert r.get_json()["analisis"] == []

    def test_listado_incluye_lo_recien_creado(self, cliente):
        creado = cliente.post("/api/analisis-energetico", json={"pais": "MX"}).get_json()
        r = cliente.get("/api/analisis-energetico")
        ids = [f["id"] for f in r.get_json()["analisis"]]
        assert creado["id"] in ids

    def test_listado_respeta_el_parametro_limite(self, cliente):
        for _ in range(3):
            cliente.post("/api/analisis-energetico", json={"pais": "CL"})
        r = cliente.get("/api/analisis-energetico?limite=1")
        assert len(r.get_json()["analisis"]) == 1

    def test_el_alias_de_listado_tambien_funciona(self, cliente):
        cliente.post("/analisis-energetico", json={"pais": "CL"})
        r = cliente.get("/analisis-energetico")
        assert r.status_code == 200
        assert len(r.get_json()["analisis"]) >= 1


class TestMismaRutaAmbosMetodos:
    def test_get_y_post_en_la_misma_ruta_no_chocan(self, cliente):
        """Confirma que fusionar GET+POST en un solo view function (necesario
        para que el contrato OpenAPI compare 1:1) no rompió ninguno de los dos."""
        r_post = cliente.post("/api/analisis-energetico", json={"pais": "CL"})
        r_get = cliente.get("/api/analisis-energetico")
        assert r_post.status_code == 200
        assert r_get.status_code == 200
        assert "id" in r_post.get_json()
        assert "analisis" in r_get.get_json()
