import unittest
from app.routers.recomendar import ordenar_resultados, limitar_con_empates
from app.comercial import enriquecer
from app.recomendador import Preferencias, CRITERIOS, criterios_seleccionados, evaluar_equipo


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

    def test_real_commercial_references_sort_mars_before_jupiter_only_on_tie(self):
        rows=[self.row('GNSS-SINOGNSS-JUPITER','SinoGNSS',2025),
              self.row('GNSS-SINOGNSS-MARS-PRO','SinoGNSS',2023),
              self.row('GNSS-SINGULARXYZ-X1','SingularXYZ',2023)]
        for row in rows:row['equipo']=enriquecer(row['equipo'])
        ordenar_resultados(rows)
        self.assertEqual([r['equipo']['id_equipo'] for r in rows],
                         ['GNSS-SINOGNSS-MARS-PRO','GNSS-SINOGNSS-JUPITER','GNSS-SINGULARXYZ-X1'])
        self.assertTrue(all(r['posicion']==1 for r in rows))
        # Un requisito adicional vuelve a calcular el cumplimiento: ni marca ni costo lo alteran.
        preferences=Preferencias(laser_alcance_min_m=50)
        for row,reach in zip(rows,(10,50,0)):
            row.update(evaluar_equipo(preferences,criterios_seleccionados(preferences),
                                     {c.clave:c.peso for c in CRITERIOS},{'laser_alcance_m':reach},[]))
        ordenar_resultados(rows)
        self.assertEqual(rows[0]['equipo']['id_equipo'],'GNSS-SINOGNSS-JUPITER')

    def test_better_scoring_foreign_model_precedes_preferred_brand_even_when_expensive(self):
        rows=[self.row('SINO','SinoGNSS',2025,95),self.row('OTHER','SingularXYZ',2023,100)]
        rows[0]['equipo']['referencia_precio']={'precio_usd':100,'comparable':True}
        rows[1]['equipo']['referencia_precio']={'precio_usd':10000,'comparable':True}
        ordenar_resultados(rows)
        self.assertEqual(rows[0]['equipo']['id_equipo'],'OTHER')

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
