from unittest import TestCase
from decimal import Decimal
from app.recomendador import Preferencias, CRITERIOS, criterios_seleccionados, evaluar_equipo

class PrecisionTests(TestCase):
    datos={'rtk_horizontal_mm':Decimal('8'),'rtk_vertical_mm':Decimal('15'),
        'rtk_ppm_h':Decimal('1'),'rtk_ppm_v':Decimal('1'),
        'red_rtk_horizontal_mm':Decimal('8'),'red_rtk_vertical_mm':Decimal('15'),
        'red_rtk_ppm_h':Decimal('0.5'),'red_rtk_ppm_v':Decimal('0.5'),
        'static_horizontal_mm':2.5,'static_vertical_mm':5,'static_ppm_h':0.5,'static_ppm_v':0.5,
        'largo_static_horizontal_mm':3,'largo_static_vertical_mm':3.5,'largo_static_ppm_h':0.1,'largo_static_ppm_v':0.4,
        'cantidad_baterias':2,'lemo_pines':7,'lemo':True}
    def evaluar(self, **values):
        p=Preferencias(**values)
        return evaluar_equipo(p,criterios_seleccionados(p),{c.clave:c.peso for c in CRITERIOS},self.datos,[])

    def test_mars_network_exact_thresholds_all_meet(self):
        r=self.evaluar(rtk_modo='red',rtk_horizontal_max_mm=8,rtk_vertical_max_mm=15,rtk_ppm_h_max=0.5,rtk_ppm_v_max=0.5)
        self.assertEqual(r['porcentaje'],100)
        self.assertEqual(r['cumplimientos'],4)

    def test_single_baseline_keeps_one_ppm(self):
        r=self.evaluar(rtk_horizontal_max_mm=8,rtk_vertical_max_mm=15,rtk_ppm_h_max=0.5,rtk_ppm_v_max=0.5)
        self.assertEqual([d['estado'] for d in r['detalle']],['incumple','incumple','cumple','cumple'])
        self.assertIn('RTK horizontal (ppm)',r['explicacion'])
        self.assertIn('RTK horizontal (mm)',r['explicacion'])

    def test_long_static_does_not_mix_with_fast_static(self):
        r=self.evaluar(static_modo='largo',static_horizontal_max_mm=3,static_vertical_max_mm=3.5,static_ppm_h_max=0.1,static_ppm_v_max=0.4)
        self.assertEqual(r['porcentaje'],100)
        self.assertGreater(self.evaluar(static_vertical_max_mm=3.5)['incumplimientos'],0)

    def test_battery_count_and_exact_lemo_pins(self):
        self.assertEqual(self.evaluar(cantidad_baterias_min=2,lemo_pines=7)['porcentaje'],100)
        self.assertEqual(self.evaluar(lemo_pines=5)['porcentaje'],0)

    def test_unknown_network_stays_unknown(self):
        p=Preferencias(rtk_modo='red',rtk_ppm_h_max=0.5)
        r=evaluar_equipo(p,criterios_seleccionados(p),{c.clave:c.peso for c in CRITERIOS},{'rtk_ppm_h':0.5},[])
        self.assertEqual(r['sin_datos'],1)
