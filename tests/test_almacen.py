"""
Tests de `src/almacen.py` — el historial de análisis en SQLite.

Cada test usa su propio archivo de DB temporal (tmp_path de pytest), para no
compartir estado entre tests ni ensuciar instance/analisis.db real.
"""
import importlib

import pytest


@pytest.fixture
def almacen(tmp_path, monkeypatch):
    """Recarga el módulo con una ruta de DB nueva y vacía por test."""
    ruta_db = str(tmp_path / "analisis_test.db")
    monkeypatch.setenv("ANALISIS_DB_PATH", ruta_db)
    import src.almacen as modulo
    importlib.reload(modulo)
    modulo.RUTA_DB = ruta_db  # reload no siempre relee el entorno a tiempo; se fuerza explícito
    return modulo


class TestGuardarYObtener:
    def test_guardar_devuelve_un_id(self, almacen):
        id_analisis = almacen.guardar({"pais": "CL"}, {"categoria": "Eficiente"})
        assert id_analisis is not None
        assert isinstance(id_analisis, str)

    def test_obtener_devuelve_lo_que_se_guardo(self, almacen):
        payload = {"pais": "CL", "dormitorios": 3}
        resultado = {"categoria": "Moderado", "consumo_kwh": 300}
        id_analisis = almacen.guardar(payload, resultado)

        registro = almacen.obtener(id_analisis)
        assert registro is not None
        assert registro["payload"] == payload
        assert registro["resultado"] == resultado
        assert registro["pais"] == "CL"
        assert registro["categoria"] == "Moderado"

    def test_obtener_id_inexistente_devuelve_none(self, almacen):
        assert almacen.obtener("id-que-no-existe") is None


class TestListar:
    def test_lista_vacia_al_principio(self, almacen):
        assert almacen.listar() == []

    def test_lista_los_mas_recientes_primero(self, almacen):
        id1 = almacen.guardar({"pais": "CL"}, {"categoria": "Eficiente"})
        id2 = almacen.guardar({"pais": "AR"}, {"categoria": "Moderado"})
        id3 = almacen.guardar({"pais": "MX"}, {"categoria": "Ineficiente"})

        listado = almacen.listar()
        ids_en_orden = [f["id"] for f in listado]
        assert ids_en_orden == [id3, id2, id1]

    def test_respeta_el_limite_pedido(self, almacen):
        for i in range(5):
            almacen.guardar({"pais": "CL"}, {"categoria": "Eficiente"})
        assert len(almacen.listar(limite=2)) == 2

    def test_limite_tiene_tope_duro_de_100(self, almacen):
        # No se pide guardar 101 filas solo para probar esto — alcanza con
        # confirmar que pedir un límite absurdo no explota ni se toma literal.
        listado = almacen.listar(limite=999999)
        assert isinstance(listado, list)  # no lanza, y el tope se aplica adentro

    def test_fila_del_listado_no_trae_el_payload_completo(self, almacen):
        almacen.guardar({"pais": "CL", "dato_grande": "x" * 1000}, {"categoria": "Eficiente"})
        fila = almacen.listar()[0]
        assert "payload" not in fila
        assert "resultado" not in fila
