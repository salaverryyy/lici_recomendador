import unittest
from unittest.mock import patch
from app import ia
from app.recomendador import Preferencias, CRITERIOS, criterios_seleccionados, evaluar_equipo
from app.controladoras import evaluate as controller_evaluate


def evaluate(p,data):
    return evaluar_equipo(p,criterios_seleccionados(p),{c.clave:c.peso for c in CRITERIOS},data,[])


class CargaLTECoverageTests(unittest.TestCase):
    def test_adapter_transfers_files_but_fails_required_charging(self):
        result=evaluate(Preferencias(usb_c=True,carga_usb_c=True),{
            'usb_c':False,'usb_c_con_adaptador':True,'lemo_solo_datos':True})
        details={d['clave']:d for d in result['detalle']}
        self.assertEqual(details['usb_c']['estado'],'cumple')
        self.assertEqual(details['carga_usb_c']['estado'],'incumple')
        self.assertIn('solo de datos',details['usb_c']['observacion'])
        self.assertLess(result['porcentaje'],100)

    def test_native_port_does_not_imply_charging(self):
        self.assertEqual(evaluate(Preferencias(carga_usb_c=True),{'usb_c':True})['sin_datos'],1)
        self.assertEqual(evaluate(Preferencias(carga_usb_c=True),{'carga_usb_c':True})['porcentaje'],100)

    def test_shared_link_only_passes_when_explicitly_allowed_and_documented(self):
        data={'lte_4g':False,'sim_fisica':False,'internet_compartido':True}
        self.assertEqual(evaluate(Preferencias(lte_4g=True),data)['porcentaje'],0)
        result=evaluate(Preferencias(lte_4g=True,lte_permite_compartido=True),data)
        self.assertEqual(result['porcentaje'],100)
        self.assertTrue(result['detalle'][0]['requiere_enlace_compartido'])
        self.assertIn('compartido',result['detalle'][0]['nombre'])
        self.assertIn('4G/LTE',result['detalle'][0]['observacion'])

    def test_bluetooth_is_not_evidence_of_shared_internet(self):
        result=evaluate(Preferencias(lte_4g=True,lte_permite_compartido=True),{
            'lte_4g':False,'bluetooth':True,'wifi':True})
        self.assertEqual(result['sin_datos'],1)
        self.assertEqual(result['porcentaje'],0)

    def test_explicit_tender_requirements_are_not_silently_dropped(self):
        raw={'tipo_equipo':'kit','intencion':'recomendacion','requisitos':{},
             'componentes':{'gnss':{'temperatura_operacion_min_c':-40,'temperatura_operacion_max_c':60,'proteccion_ip_aceptada':'IP67,IP68'},'controladora':{'proteccion_ip':'IP67'}},
             'respuesta_general':'','preguntas':['¿LTE integrado o compartido?'],'omitidos':[]}
        text='''Módem celular integrado o mediante enlace compartido compatible con 4G/LTE.
        Puerto USB Tipo-C que soporte carga de energía y transferencia de datos directa.
        Formatos RINEX versiones 2.x y 3.x. NTRIP y WebUI, RTCM 2.x, 3.x, CMR y CMR+.
        Frecuencias mínimas GPS L1 L2 L5, Galileo E1 E5a E5b.
        CARACTERÍSTICAS FÍSICAS (RECEPTORES Y COLECTORAS): caídas sobre concreto desde
        una altura de 2.0 metros (en bastón para los receptores), MIL-STD-810G.'''
        with patch.object(ia,'quota_until',return_value=None),patch.object(ia,'_post_gemini',return_value=(raw,{})):
            parsed=ia.interpret(text)
        req=parsed['componentes']['gnss']
        self.assertTrue(req['lte_4g'])
        self.assertTrue(req['lte_permite_compartido'])
        self.assertTrue(req['carga_usb_c'])
        self.assertTrue(req['registro_rinex_3'])
        self.assertEqual(req['caida_min_m'],2)
        self.assertEqual(req['vibracion_norma'],'MIL-STD-810G')
        ctrl=parsed['componentes']['controladora']
        self.assertEqual(ctrl['temperatura_operacion_min_c'],-40)
        self.assertEqual(ctrl['caida_m'],2)
        self.assertEqual(ctrl['proteccion_ip'],'IP67;IP68')
        self.assertFalse(parsed['preguntas'])
        self.assertTrue(any('NTRIP' in item for item in parsed['omitidos']))
        self.assertTrue(any('señales' in item for item in parsed['omitidos']))

    def test_controller_accepts_either_explicit_ip_option(self):
        for value in ('IP67','IP68'):
            self.assertEqual(controller_evaluate({'proteccion_ip':value},{'proteccion_ip':'IP67;IP68'})['porcentaje'],100)
        self.assertEqual(controller_evaluate({'proteccion_ip':'IP65'},{'proteccion_ip':'IP67;IP68'})['porcentaje'],0)
