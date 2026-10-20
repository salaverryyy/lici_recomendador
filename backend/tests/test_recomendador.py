import unittest
from pydantic import ValidationError
from app.recomendador import CRITERIOS, Preferencias, criterios_seleccionados, evaluar_equipo


def evaluar(preferencias, datos):
    return evaluar_equipo(preferencias, criterios_seleccionados(preferencias),
                          {c.clave:c.peso for c in CRITERIOS}, datos, [])


class RecomendadorTests(unittest.TestCase):
    def test_dos_camaras_reciben_mas_puntos_si_se_piden_dos(self):
        p=Preferencias(cantidad_camaras_min=2)
        self.assertEqual(evaluar(p, {"cantidad_camaras":2})["porcentaje"],100)
        partial = evaluar(p, {"cantidad_camaras":1})
        self.assertEqual(partial["porcentaje"],0)
        self.assertEqual(partial["porcentaje_afinidad"],50)
        self.assertEqual(evaluar(p, {})["sin_datos"],1)

    def test_camara_booleana_no_inventa_bonificaciones(self):
        p=Preferencias(necesita_camara=True)
        self.assertEqual(evaluar(p,{"tiene_camara":True,"cantidad_camaras":1})["porcentaje"],
                         evaluar(p,{"tiene_camara":True,"cantidad_camaras":2})["porcentaje"])

    def test_protocolo_conocido_y_desconocido(self):
        p=Preferencias(necesita_snlonglink=True)
        self.assertEqual(evaluar(p,{"tiene_snlonglink":True})["porcentaje"],100)
        self.assertEqual(evaluar(p,{"tiene_snlonglink":False})["incumplimientos"],1)
        self.assertEqual(evaluar(p,{})["sin_datos"],1)

    def test_ppm_horizontal_y_vertical_distintos(self):
        p=Preferencias(static_ppm_h_max=0.1,static_ppm_v_max=0.4)
        self.assertEqual(evaluar(p,{"static_ppm_h":0.1,"static_ppm_v":0.4})["porcentaje"],100)
        partial = evaluar(p,{"static_ppm_h":0.1,"static_ppm_v":0.5})
        self.assertEqual(partial["porcentaje"],50)
        self.assertEqual(partial["porcentaje_afinidad"],90)

    def test_an_unrequested_feature_cannot_improve_tender_compliance(self):
        p = Preferencias(usb_c=True, memoria_min_gb=8)
        basic = evaluar(p, {'usb_c': True, 'memoria': 8})
        advanced = evaluar(p, {'usb_c': True, 'memoria': 8, 'laser': True, 'cantidad_camaras': 2})
        self.assertEqual(basic['porcentaje'], advanced['porcentaje'])

    def test_failed_minimum_is_not_softened_by_proximity(self):
        result = evaluar(Preferencias(memoria_min_gb=8), {'memoria':7.99})
        self.assertEqual(result['porcentaje'],0)
        self.assertEqual(result['aptitud'],'no_cumple')
        self.assertEqual(result['cumplimientos'],0)

    def test_absent_sensor_is_noncompliance_not_an_unknown_angle(self):
        result=evaluar(Preferencias(inclinacion_imu_min_deg=60),{'tiene_imu':False})
        self.assertEqual(result['incumplimientos'],1)
        self.assertEqual(result['sin_datos'],0)

    def test_clientes_anteriores_pueden_enviar_ppm_compartido(self):
        p=Preferencias(rtk_ppm_max=0.5)
        self.assertEqual(p.rtk_ppm_h_max,0.5)
        self.assertEqual(p.rtk_ppm_v_max,0.5)
        self.assertEqual(len(criterios_seleccionados(p)),2)
        with self.assertRaises(ValidationError):
            Preferencias(rtk_ppm_max=0.5,rtk_ppm_h_max=0.1)

    def test_no_y_cantidad_fraccionaria(self):
        self.assertEqual(criterios_seleccionados(Preferencias(necesita_snlonglink=False)),[])
        with self.assertRaises(ValidationError):
            Preferencias(cantidad_camaras_min=1.5)

    def test_alcance_laser_es_independiente_de_tener_laser(self):
        p = Preferencias(laser=True, laser_alcance_min_m=50)
        self.assertEqual(evaluar(p, {'laser': True, 'laser_alcance_m': 50})['porcentaje'], 100)
        result = evaluar(p, {'laser': True, 'laser_alcance_m': 10})
        self.assertEqual(result['cumplimientos'], 1)
        self.assertEqual(result['incumplimientos'], 1)


if __name__ == "__main__":
    unittest.main()
