import unittest
from pydantic import ValidationError
from app.recomendador import Preferencias, CRITERIOS, criterios_seleccionados, evaluar_equipo


def evaluar(preferencias, datos):
    return evaluar_equipo(preferencias, criterios_seleccionados(preferencias),
                          {c.clave: c.peso for c in CRITERIOS}, datos, [])


class MemoriaConstelacionesTests(unittest.TestCase):
    def test_memoria_fabrica_y_extension(self):
        p = Preferencias(memoria_min_gb=8)
        original = evaluar(p, {"memoria": 8})
        self.assertEqual(original["porcentaje"], 100)
        self.assertNotIn("extendida", original["explicacion"])
        ampliada = evaluar(p, {"memoria": 4, "memoria_expandible": True, "memoria_expandida_max_gb": 32})
        self.assertEqual(ampliada["porcentaje"], 100)
        self.assertIn("con memoria extendida", ampliada["explicacion"])
        self.assertEqual(ampliada["detalle"][0]["memoria_fabrica_gb"], 4)
        self.assertTrue(ampliada["detalle"][0]["requiere_ampliacion"])

    def test_extension_insuficiente_desconocida_o_no_aceptada(self):
        for datos, esperado in [({"memoria": 4}, 50),
                                 ({"memoria": 4, "memoria_expandible": True}, 50),
                                 ({"memoria": 4, "memoria_expandible": False, "memoria_expandida_max_gb": 32}, 50),
                                 ({"memoria": 4, "memoria_opcional_fabrica_max_gb": 32}, 50)]:
            self.assertEqual(evaluar(Preferencias(memoria_min_gb=8), datos)["porcentaje"], esperado)
        r = evaluar(Preferencias(memoria_min_gb=64), {"memoria": 4, "memoria_expandible": True, "memoria_expandida_max_gb": 32})
        self.assertEqual(r["porcentaje"], 50)
        self.assertNotIn("Cumple:", r["explicacion"])
        self.assertEqual(evaluar(Preferencias(memoria_min_gb=8), {})["sin_datos"], 1)

    def test_constelaciones_especificas_y_sbas(self):
        p = Preferencias(gps=True, galileo=True, sbas=True, qzss=False)
        self.assertEqual({c.clave for c in criterios_seleccionados(p)}, {"gps", "galileo", "sbas"})
        r = evaluar(p, {"gps": True, "galileo": False, "sbas": None, "constelaciones": 6})
        self.assertEqual((r["cumplimientos"], r["incumplimientos"], r["sin_datos"]), (1, 1, 1))

    def test_generacion_exacta_y_no_inferida_desde_tecnologia(self):
        p = Preferencias(imu_generacion="3ª generación")
        self.assertEqual(evaluar(p, {"imu_generacion": "3ª generación"})["porcentaje"], 100)
        self.assertEqual(evaluar(p, {"imu_tecnologia": "Auto-IMU"})["sin_datos"], 1)

    def test_comunicaciones_seleccionadas_y_potencia(self):
        p = Preferencias(wifi=True, lte_4g=False, radio_potencia_min_w=2)
        r = evaluar(p, {"wifi": True, "radio_potencia_max_w": 1})
        self.assertEqual(r["cumplimientos"], 1)
        self.assertEqual(r["incumplimientos"], 1)
        with self.assertRaises(ValidationError):
            Preferencias(radio_potencia_min_w=-1)
