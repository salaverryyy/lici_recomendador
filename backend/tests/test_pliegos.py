import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from app import ia
from app.pliegos import extraer_pliego
from app.soluciones import assemble, unscored

TEXT = (Path(__file__).parent/'fixtures/pliego_gnss.txt').read_text(encoding='utf-8')


class PliegosTests(unittest.TestCase):
    def test_different_provider_extractions_produce_same_explicit_requirements(self):
        outputs = [
            {'tipo_equipo':'kit','intencion':'recomendacion','componentes':{'gnss':{'canales_min':220}}},
            {'tipo_equipo':'gnss','intencion':'consulta_catalogo','requisitos':{'memoria_min_gb':16,'temperatura_operacion_max_c':65},'componentes':{'controladora':{'ram_gb':8}}},
        ]
        results = []
        for i, raw in enumerate(outputs):
            with patch.object(ia,'quota_until',return_value=None), patch.object(ia,'_post_gemini',return_value=(copy.deepcopy(raw),{'_model':f'model-{i}'})):
                results.append(ia.interpret(TEXT,workflow_context={'componentes':{'gnss':{'laser':True}},'selecciones':{'gnss':'X1'}}))
        self.assertEqual(results[0]['componentes'],results[1]['componentes'])
        self.assertEqual(results[0]['tipo_equipo'],'kit')
        self.assertTrue(results[0]['misma_marca'])
        self.assertEqual(results[0]['selecciones'],{})
        req=results[0]['componentes']['gnss']
        self.assertEqual(req['temperatura_operacion_max_c'],55)
        self.assertEqual(req['memoria_min_gb'],32)
        self.assertEqual(req['peso_max_g'],2200)
        self.assertTrue(req['carga_usb_c'])
        self.assertEqual(results[0]['componentes']['controladora']['caida_m'],2)
        self.assertNotIn('ram_gb',results[0]['componentes']['controladora'])
        self.assertFalse(any('misma marca' in q for q in results[0]['preguntas']))

    def test_other_thresholds_are_read_from_text_not_the_example(self):
        result=extraer_pliego(TEXT.replace('512 canales','768 canales').replace('32 GB','64 GB').replace('400 MHz a 480 MHz','420 MHz a 460 MHz'))
        req=result['componentes']['gnss']
        self.assertEqual(req['canales_min'],768)
        self.assertEqual(req['memoria_min_gb'],64)
        self.assertEqual((req['radio_min_mhz'],req['radio_max_mhz']),(420,460))

    def test_short_comparison_does_not_enter_tender_parser(self):
        self.assertIsNone(extraer_pliego('¿Por qué la R80 y no la R60?'))

    def test_partial_unknown_kit_does_not_outrank_more_verified_compliance(self):
        def receiver(ident,brand,score,states):
            row=unscored({'id_equipo':ident,'marca':brand,'modelo':ident})
            row.update(porcentaje=score,detalle=[{'estado':s} for s in states])
            return row
        known=receiver('Jupiter','SinoGNSS',83.33,['cumple','incumple'])
        unknown=receiver('Z1','SingularXYZ',53.62,['cumple','sin_datos'])
        options=assemble([unknown,known],[],[],{}, {})['opciones']
        self.assertEqual(options[0]['gnss']['equipo']['id_equipo'],'Jupiter')
        self.assertEqual(options[0]['estado'],'no_cumple')
        self.assertEqual(options[1]['sin_datos'],1)

    def test_better_actual_compliance_beats_brand_preference(self):
        a=unscored({'id_equipo':'A','marca':'SinoGNSS'})
        b=unscored({'id_equipo':'B','marca':'SingularXYZ'})
        a.update(porcentaje=50,detalle=[{'estado':'incumple'}])
        b.update(porcentaje=100,detalle=[{'estado':'cumple'}])
        self.assertEqual(assemble([a,b],[],[],{}, {})['opciones'][0]['gnss']['equipo']['id_equipo'],'B')


if __name__=='__main__':unittest.main()
