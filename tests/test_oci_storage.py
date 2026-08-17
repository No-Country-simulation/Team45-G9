"""
Tests de `src/oci_storage.py`.

Ninguno de estos toca la red de verdad ni necesita credenciales — se prueba
la lógica de degradación (Fase E, mismo espíritu que src/geo.py con
Nominatim), no la conexión real a un bucket.
"""
import importlib

import pytest

import src.oci_storage as oci_storage


@pytest.fixture(autouse=True)
def recargar_modulo(monkeypatch):
    """Cada test parte limpio: sin variables de entorno de OCI heredadas de
    otro test o del entorno real."""
    for var in ("OCI_BUCKET_NAMESPACE", "OCI_BUCKET_NAME", "OCI_MODEL_OBJECT", "OCI_METADATOS_OBJECT"):
        monkeypatch.delenv(var, raising=False)
    importlib.reload(oci_storage)
    yield
    importlib.reload(oci_storage)


class TestOciConfigurado:
    def test_sin_ninguna_variable_no_esta_configurado(self):
        assert oci_storage.oci_configurado() is False

    def test_con_namespace_pero_sin_bucket_no_esta_configurado(self, monkeypatch):
        monkeypatch.setenv("OCI_BUCKET_NAMESPACE", "mi-namespace")
        importlib.reload(oci_storage)
        assert oci_storage.oci_configurado() is False

    def test_con_ambas_variables_si_esta_configurado(self, monkeypatch):
        monkeypatch.setenv("OCI_BUCKET_NAMESPACE", "mi-namespace")
        monkeypatch.setenv("OCI_BUCKET_NAME", "mi-bucket")
        importlib.reload(oci_storage)
        assert oci_storage.oci_configurado() is True


class TestSincronizarModeloDegradaSinRomper:
    def test_sin_oci_configurado_no_intenta_nada(self, tmp_path):
        ruta_modelo = str(tmp_path / "modelo.joblib")
        ruta_metadatos = str(tmp_path / "metadatos.json")

        estado = oci_storage.sincronizar_modelo(ruta_modelo, ruta_metadatos)

        assert estado["oci_configurado"] is False
        assert estado["descargado_de_oci"] is False

    def test_si_el_modelo_local_ya_existe_no_intenta_descargar(self, tmp_path, monkeypatch):
        monkeypatch.setenv("OCI_BUCKET_NAMESPACE", "ns")
        monkeypatch.setenv("OCI_BUCKET_NAME", "bucket")
        importlib.reload(oci_storage)

        ruta_modelo = tmp_path / "modelo.joblib"
        ruta_modelo.write_bytes(b"contenido de prueba")
        ruta_metadatos = str(tmp_path / "metadatos.json")

        estado = oci_storage.sincronizar_modelo(str(ruta_modelo), ruta_metadatos)

        assert estado["modelo_local_ya_existia"] is True
        assert estado["descargado_de_oci"] is False
        # El archivo no se tocó — sigue con el contenido de prueba, no algo
        # que hubiera intentado sobreescribir.
        assert ruta_modelo.read_bytes() == b"contenido de prueba"

    def test_configurado_pero_sin_credenciales_reales_degrada_sin_lanzar(self, tmp_path, monkeypatch):
        """Sin ~/.oci/config ni Instance Principal disponibles (el caso de
        cualquier entorno de CI/tests), _obtener_cliente() debe devolver None
        y sincronizar_modelo() debe devolver un estado, nunca lanzar."""
        monkeypatch.setenv("OCI_BUCKET_NAMESPACE", "ns")
        monkeypatch.setenv("OCI_BUCKET_NAME", "bucket")
        importlib.reload(oci_storage)

        ruta_modelo = str(tmp_path / "no_existe_todavia.joblib")
        ruta_metadatos = str(tmp_path / "metadatos.json")

        estado = oci_storage.sincronizar_modelo(ruta_modelo, ruta_metadatos)

        assert estado["oci_configurado"] is True
        assert estado["descargado_de_oci"] is False  # no hay credenciales reales en este entorno
