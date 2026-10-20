import unittest
from app.routers.recomendar import ordenar_resultados, limitar_con_empates


class EmpatesTest(unittest.TestCase):
    def test_limit_preserves_all_products_tied_at_boundary(self):
        rows=[{'equipo':{'id_equipo':str(i)},'porcentaje':p,'sin_datos':0,'cumplimientos':1}
              for i,p in enumerate([100,100,100,100,90,90,80])]
        ordenar_resultados(rows)
        self.assertEqual(len(limitar_con_empates(rows,2)),4)
        self.assertEqual(len(limitar_con_empates(rows,5)),6)
        self.assertEqual(len(limitar_con_empates(rows,20)),7)
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
