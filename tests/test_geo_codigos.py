"""
Tests de src/geo_codigos.py — el texto libre de provincia/estado (ya sea
autodetectado por geolocalización o escrito a mano) traducido al código
numérico exacto que necesita el modelo de eficiencia real.
"""
from src import geo_codigos as gc


class TestEstadosUsa:
    def test_nombre_completo_con_mayusculas_exactas(self):
        assert gc.mapear_estado("US", "California") == 5

    def test_nombre_completo_en_minusculas(self):
        assert gc.mapear_estado("US", "california") == 5

    def test_abreviatura_de_dos_letras(self):
        assert gc.mapear_estado("US", "CA") == 5
        assert gc.mapear_estado("US", "ca") == 5

    def test_nombre_con_dos_palabras(self):
        assert gc.mapear_estado("US", "New York") == 33
        assert gc.mapear_estado("US", "new york") == 33

    def test_district_of_columbia(self):
        assert gc.mapear_estado("US", "District of Columbia") == 9
        assert gc.mapear_estado("US", "DC") == 9


class TestProvinciasChile:
    def test_provincia_con_tilde(self):
        assert gc.mapear_estado("CL", "Valparaíso") == 14

    def test_provincia_sin_tilde(self):
        assert gc.mapear_estado("CL", "valparaiso") == 14

    def test_santiago(self):
        assert gc.mapear_estado("CL", "Santiago") == 22
        assert gc.mapear_estado("CL", "santiago") == 22

    def test_nombre_con_apostrofo_y_espacios(self):
        assert gc.mapear_estado("CL", "O'Higgins") == 28

    def test_nombre_sin_apostrofo_ni_espacio(self):
        """Caso real reportado: alguien escribe 'ohiggins' corrido, sin
        apóstrofo ni espacio — tiene que igual reconocerlo."""
        assert gc.mapear_estado("CL", "ohiggins") == 28


class TestRegionCompletaDeGeolocalizacion:
    """La geolocalización real (Nominatim) da el nombre de la REGIÓN, más
    ancha que la provincia — tiene que mapear a una provincia representante."""

    def test_region_de_ohiggins_tal_cual_la_da_nominatim(self):
        texto_real = "Región del Libertador General Bernardo O'Higgins"
        assert gc.mapear_estado("CL", texto_real) == 28

    def test_region_metropolitana(self):
        assert gc.mapear_estado("CL", "Región Metropolitana") == 22
        assert gc.mapear_estado("CL", "Metropolitana de Santiago") == 22


class TestPaisesSinModeloPropio:
    def test_brasil_no_tiene_codigo_nunca(self):
        assert gc.mapear_estado("BR", "São Paulo") is None

    def test_argentina_no_tiene_codigo_nunca(self):
        assert gc.mapear_estado("AR", "Buenos Aires") is None


class TestTextoIrreconocible:
    def test_texto_sin_sentido_devuelve_none_sin_lanzar(self):
        assert gc.mapear_estado("CL", "esto no es ninguna provincia") is None

    def test_texto_vacio_devuelve_none(self):
        assert gc.mapear_estado("US", "") is None

    def test_pais_vacio_devuelve_none(self):
        assert gc.mapear_estado("", "California") is None
