"""
Tests de `_recomendaciones_contextuales`: los umbrales proporcionales
portados desde el motor de G9 (docs/reglas_recomendaciones.md), no la
presencia/ausencia plana de un artefacto.
"""
import app as aplicacion


def _perfil(desglose: dict) -> dict:
    """Arma un `perfil` mínimo como el que devuelve estimar_desde_perfil()."""
    return {"desglose": desglose, "items": list(desglose.keys()), "ahorro_dinero_mes": 0}


class TestUmbralVentanas:
    def test_ventanas_sobre_3x_dormitorios_dispara_la_recomendacion(self):
        d = {"dormitorios": 2, "ventanas": 7, "agua_caliente_electrica": 0, "secarropas_electrico": 0,
             "lavado_frecuencia": 0, "refrigerador": 1, "freezer": 0, "tv_frecuencia": 0, "horno_electrico": 0}
        recs = aplicacion._recomendaciones_contextuales("Moderado", d, _perfil({}))
        assert any("ventanas" in r.lower() for r in recs)

    def test_ventanas_bajo_3x_dormitorios_no_dispara(self):
        d = {"dormitorios": 3, "ventanas": 6, "agua_caliente_electrica": 0, "secarropas_electrico": 0,
             "lavado_frecuencia": 0, "refrigerador": 1, "freezer": 0, "tv_frecuencia": 0, "horno_electrico": 0}
        recs = aplicacion._recomendaciones_contextuales("Moderado", d, _perfil({}))
        assert not any("ventanas" in r.lower() for r in recs)

    def test_monoambiente_no_revienta_por_division_cero(self):
        """dormitorios=0 (monoambiente) no debe romper el cálculo 3x dormitorios."""
        d = {"dormitorios": 0, "ventanas": 5, "agua_caliente_electrica": 0, "secarropas_electrico": 0,
             "lavado_frecuencia": 0, "refrigerador": 1, "freezer": 0, "tv_frecuencia": 0, "horno_electrico": 0}
        recs = aplicacion._recomendaciones_contextuales("Moderado", d, _perfil({}))
        assert isinstance(recs, list)  # no lanza excepción


class TestUmbralCalefaccionYSecarropas:
    def test_calefaccion_sobre_10_por_ciento_dispara_recomendacion(self):
        d = {"dormitorios": 1, "ventanas": 1, "agua_caliente_electrica": 0, "secarropas_electrico": 0,
             "lavado_frecuencia": 0, "refrigerador": 1, "freezer": 0, "tv_frecuencia": 0, "horno_electrico": 0}
        perfil = _perfil({"Calefactor eléctrico": 50, "Refrigerador": 50})  # 50% del total
        recs = aplicacion._recomendaciones_contextuales("Moderado", d, perfil)
        assert any("calefacción" in r.lower() for r in recs)

    def test_calefaccion_con_mas_de_2_dormitorios_agrega_recomendacion_extra(self):
        d = {"dormitorios": 3, "ventanas": 1, "agua_caliente_electrica": 0, "secarropas_electrico": 0,
             "lavado_frecuencia": 0, "refrigerador": 1, "freezer": 0, "tv_frecuencia": 0, "horno_electrico": 0}
        perfil = _perfil({"Calefactor eléctrico": 50, "Refrigerador": 50})
        recs = aplicacion._recomendaciones_contextuales("Moderado", d, perfil)
        assert any("cerrados" in r.lower() for r in recs)

    def test_secarropas_con_2_5_o_mas_lavados_semana_dispara_recomendacion(self):
        d = {"dormitorios": 1, "ventanas": 1, "agua_caliente_electrica": 0, "secarropas_electrico": 1,
             "lavado_frecuencia": 3, "refrigerador": 1, "freezer": 0, "tv_frecuencia": 0, "horno_electrico": 0}
        recs = aplicacion._recomendaciones_contextuales("Moderado", d, _perfil({"Secadora de ropa": 20}))
        assert any("secarropas" in r.lower() for r in recs)

    def test_secarropas_con_menos_de_2_5_lavados_no_dispara(self):
        d = {"dormitorios": 1, "ventanas": 1, "agua_caliente_electrica": 0, "secarropas_electrico": 1,
             "lavado_frecuencia": 1, "refrigerador": 1, "freezer": 0, "tv_frecuencia": 0, "horno_electrico": 0}
        recs = aplicacion._recomendaciones_contextuales("Moderado", d, _perfil({"Secadora de ropa": 20}))
        assert not any("secarropas eléctrico representa" in r.lower() for r in recs)


class TestSiempreIncluye:
    def test_incluye_mensaje_de_categoria_al_inicio(self):
        d = {"dormitorios": 1, "ventanas": 1, "agua_caliente_electrica": 0, "secarropas_electrico": 0,
             "lavado_frecuencia": 0, "refrigerador": 1, "freezer": 0, "tv_frecuencia": 0, "horno_electrico": 0}
        recs = aplicacion._recomendaciones_contextuales("Eficiente", d, _perfil({}))
        assert "eficiente" in recs[0].lower()

    def test_maximo_8_recomendaciones(self):
        d = {"dormitorios": 1, "ventanas": 10, "agua_caliente_electrica": 1, "secarropas_electrico": 1,
             "lavado_frecuencia": 5, "refrigerador": 2, "freezer": 1, "tv_frecuencia": 10, "horno_electrico": 1}
        perfil = _perfil({
            "Aire acondicionado": 15, "Calefactor eléctrico": 15,
            "Termotanque / calentador de agua electrico": 15, "Secadora de ropa": 15,
        })
        recs = aplicacion._recomendaciones_contextuales("Ineficiente", d, perfil)
        assert len(recs) <= 8
