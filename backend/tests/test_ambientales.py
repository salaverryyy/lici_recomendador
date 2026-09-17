import unittest
from fastapi import HTTPException
from app.routers.admin_equipos import validar_especificaciones


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
