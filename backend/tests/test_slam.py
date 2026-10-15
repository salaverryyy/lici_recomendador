import unittest

from fastapi import HTTPException

from app.slam import evaluate, validate


class SlamTests(unittest.TestCase):
    def test_licitacion_de_ejemplo_distingue_cumplimiento(self):
        requirements = {
            "puntos_por_segundo": 200_000,
            "alcance_lidar_m": 70,
            "precision_nube_cm": 3,
            "laser_clase_1": True,
            "autonomia_h": 2,
            "proteccion_ip": "IP54",
        }
        result = evaluate(
            {
                "puntos_por_segundo": 200_000,
                "alcance_lidar_m": 70,
                "precision_nube_cm": 1,
                "laser_clase_1": True,
                "autonomia_h": 2,
                "proteccion_ip": "IP54",
            },
            requirements,
        )
        self.assertEqual(result["porcentaje"], 100)
        self.assertEqual(result["cumplimientos"], 6)

    def test_gnss_opcional_no_se_confunde_con_integrado(self):
        result = evaluate(
            {"gnss_disponible": True, "gnss_integrado": False, "gnss_opcional": True},
            {"gnss_integrado": True},
        )
        self.assertEqual(result["detalle"][0]["estado"], "no_cumple")

    def test_aplicacion_se_evalua_como_opcion_normalizada(self):
        result = evaluate(
            {"aplicaciones": "Interiores;Minería;Modelado 3D"},
            {"aplicaciones": "mineria"},
        )
        self.assertEqual(result["porcentaje"], 100)

    def test_ip_superior_cumple_minimo(self):
        self.assertEqual(
            evaluate({"proteccion_ip": "IP65"}, {"proteccion_ip": "IP54"})["porcentaje"],
            100,
        )

    def test_rechaza_campo_inventado(self):
        with self.assertRaises(HTTPException):
            validate({"campo_inventado": 1}, requirements=True)


if __name__ == "__main__":
    unittest.main()
