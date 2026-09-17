import unittest
from fastapi import HTTPException
from app.routers.admin_equipos import validar_especificaciones
from app.recomendador import Preferencias, CRITERIOS, criterios_seleccionados, evaluar_equipo
from pydantic import ValidationError


def puntuar(p, datos):
    return evaluar_equipo(p, criterios_seleccionados(p),
                          {c.clave: c.peso for c in CRITERIOS}, datos, [])


class AmbientalesTests(unittest.TestCase):
    def test_temperaturas_negativas_y_ip_multiple(self):
        validar_especificaciones({"temperatura_operacion_min_c": -45,
                                 "proteccion_ip": "IP66 | IP68",
                                 "humedad_max_pct": 100,
                                 "caida_m": 1.2})

    def test_valores_imposibles_y_tipos_incorrectos(self):
        for cambios in ({"temperatura_operacion_min_c": -300},
                        {"temperatura_operacion_min_c": float("nan")},
                        {"temperatura_operacion_max_c": True},
                        {"humedad_max_pct": 101}, {"caida_m": -1},
                        {"proteccion_ip": "IP99"}):
            with self.subTest(cambios=cambios), self.assertRaises(HTTPException):
                validar_especificaciones(cambios)

    def test_datos_desconocidos_permiten_null(self):
        validar_especificaciones({"humedad_max_pct": None,
                                 "temperatura_almacenamiento_min_c": None})

    def test_rango_termico_negativo_y_restriccion_de_camara(self):
        datos = {"temperatura_operacion_min_c": -40, "temperatura_operacion_max_c": 65,
                 "temperatura_camara_min_c": -30, "temperatura_camara_max_c": 50,
                 "tiene_camara": True}
        p = Preferencias(temperatura_operacion_min_c=-40, temperatura_operacion_max_c=65)
        self.assertEqual(puntuar(p, datos)["porcentaje"], 100)
        p = Preferencias(temperatura_operacion_min_c=-40, temperatura_operacion_max_c=65, necesita_camara=True)
        self.assertEqual(puntuar(p, datos)["incumplimientos"], 2)
        self.assertEqual(puntuar(p, datos)["detalle"][0]["valor_equipo"], -30)

    def test_ip_no_infiere_equivalencias(self):
        p = Preferencias(proteccion_ip_aceptada="IP66,IP67")
        self.assertEqual(puntuar(p, {"proteccion_ip": "IP68"})["porcentaje"], 0)
        self.assertEqual(puntuar(p, {"proteccion_ip": "IP66 | IP68"})["porcentaje"], 100)
        self.assertEqual(puntuar(p, {})["sin_datos"], 1)

    def test_version_de_norma_y_condensacion(self):
        p = Preferencias(vibracion_norma="MIL-STD-810G", humedad_condicion="Con condensación")
        d = {"vibracion_norma": "MIL-STD-810G Method 514.6 procedure", "humedad_condicion": "Sin condensación"}
        self.assertEqual(puntuar(p, d)["cumplimientos"], 1)
        d["vibracion_norma"] = "MIL-STD-810H"
        self.assertEqual(puntuar(p, d)["cumplimientos"], 0)

    def test_rechaza_rangos_invertidos_y_humedad_imposible(self):
        for valores in ({"temperatura_operacion_min_c": 30, "temperatura_operacion_max_c": -20},
                        {"humedad_min_pct": 101}):
            with self.assertRaises(ValidationError):
                Preferencias(**valores)
