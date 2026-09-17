import unittest
from app.routers.recomendar import ordenar_resultados


class EmpatesTest(unittest.TestCase):
    def test_comparten_puesto_aunque_difiera_cobertura(self):
        datos = [
            {"equipo": {"id_equipo": id}, "porcentaje": pct,
             "sin_datos": faltan, "cumplimientos": 10}
            for id, pct, faltan in [("j", 91.26, 2), ("i", 91.26, 1), ("x", 80, 0)]
        ]
        ordenar_resultados(datos)
        self.assertEqual([r["posicion"] for r in datos], [1, 1, 3])
        self.assertEqual([r["empate"] for r in datos], [True, True, False])


if __name__ == "__main__":
    unittest.main()
