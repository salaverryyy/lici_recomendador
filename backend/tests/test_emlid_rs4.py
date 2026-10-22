import json
from pathlib import Path
import unittest

from app.recomendador import Preferencias,CRITERIOS,criterios_seleccionados,evaluar_equipo
from app.cotecmi import es_cotecmi
from app.soluciones import assemble,unscored

ROOT=Path(__file__).resolve().parents[2]
DATA=json.loads((ROOT/'docs/auditoria/2026-10-22/emlid-rs4.json').read_text(encoding='utf-8'))


def evaluate(**req):
    p=Preferencias(**req)
    return evaluar_equipo(p,criterios_seleccionados(p),{c.clave:c.peso for c in CRITERIOS},DATA['evaluacion'],[])


class RS4Tests(unittest.TestCase):
    def test_native_lte_storage_and_rinex_are_supported(self):
        self.assertTrue(es_cotecmi(DATA['equipo']['marca']))
        result=evaluate(lte_4g=True,memoria_min_gb=16,memoria_solo_fabrica=True,registro_rinex_3=True,rinex_3_nativo=True,usb_c=True,carga_usb_c=True)
        self.assertEqual(result['porcentaje'],100)

    def test_static_and_rtk_precision_are_not_copied_from_rs3(self):
        self.assertEqual(evaluate(rtk_horizontal_max_mm=7,rtk_vertical_max_mm=14)['porcentaje'],100)
        self.assertEqual(evaluate(static_horizontal_max_mm=3)['incumplimientos'],1)

    def test_rs4_is_not_the_camera_equipped_pro_model(self):
        self.assertEqual(evaluate(cantidad_camaras_min=2,laser=True)['incumplimientos'],2)
        self.assertEqual(evaluate(canales_min=1400,actualizacion_min_hz=20)['incumplimientos'],2)

    def test_unlimited_tilt_is_a_declaration_not_an_invented_numeric_maximum(self):
        result=evaluate(inclinacion_imu_min_deg=60)
        self.assertEqual(result['porcentaje'],100)
        detail=result['detalle'][0]
        self.assertIsNone(detail['valor_equipo'])
        self.assertIn('sin límite angular',detail['observacion'])

    def test_unknown_rinex2_remains_unknown(self):
        self.assertEqual(evaluate(registro_rinex_2=True)['sin_datos'],1)

    def test_generic_emlid_workflow_uses_phone_and_emlid_studio(self):
        receiver=unscored(DATA['equipo'])
        software=[{'id_software':'emlid-studio','marca':'Emlid','nombre':'Emlid Studio','funciones':{},'publicado':True}]
        result=assemble([receiver],[],software,{}, {})['opciones'][0]
        self.assertIsNone(result['controladora'])
        self.assertIn('Emlid Flow',result['app_campo']['nombre'])
        self.assertEqual(result['software']['software']['nombre'],'Emlid Studio')


if __name__=='__main__':unittest.main()
