import unittest
from app.routers.recomendar import ordenar_resultados, limitar_con_empates


class EmpatesTest(unittest.TestCase):
    def row(self, ident, brand, year, percentage=100):
        return {'equipo':{'id_equipo':ident,'marca':brand,'anio_modelo':year},'porcentaje':percentage,'sin_datos':0,'cumplimientos':1}

    def test_commercial_brand_preference_then_newer_model_without_altering_positions(self):
        rows=[self.row('RS2+','Emlid',2022),self.row('RS3','Emlid',2023),self.row('MARS','SinoGNSS',2023),self.row('ORION','SingularXYZ',2024),self.row('UNKNOWN','SinoGNSS',None)]
        ordenar_resultados(rows)
        self.assertEqual([r['equipo']['id_equipo'] for r in rows],['MARS','UNKNOWN','ORION','RS3','RS2+'])
        self.assertTrue(all(r['posicion']==1 and r['empate'] for r in rows))

    def test_brand_and_year_cannot_overrule_technical_score(self):
        rows=[self.row('NEW','SinoGNSS',2025,90),self.row('OLD','SingularXYZ',2022,100)]
        ordenar_resultados(rows)
        self.assertEqual(rows[0]['equipo']['id_equipo'],'OLD')

    def test_comparable_unit_price_precedes_model_year_within_brand(self):
        rows=[self.row('ORION','SingularXYZ',2024),self.row('X1','SingularXYZ',2023)]
        rows[0]['equipo']['referencia_precio']={'precio_usd':3528.99,'comparable':True}
        rows[1]['equipo']['referencia_precio']={'precio_usd':2897.99,'comparable':True}
        ordenar_resultados(rows)
        self.assertEqual(rows[0]['equipo']['id_equipo'],'X1')
        self.assertEqual(rows[0]['posicion'],rows[1]['posicion'])

    def test_unpriced_or_noncomparable_is_not_zero_cost(self):
        rows=[self.row('UNKNOWN','SingularXYZ',2025),self.row('PRICED','SingularXYZ',2023)]
        rows[0]['equipo']['referencia_precio']={'precio_usd':1,'comparable':False}
        rows[1]['equipo']['referencia_precio']={'precio_usd':2000,'comparable':True}
        ordenar_resultados(rows)
        self.assertEqual(rows[0]['equipo']['id_equipo'],'PRICED')

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
