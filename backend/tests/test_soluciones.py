import json
import unittest
from pathlib import Path
from unittest.mock import patch
from app import ia
from app.software import rank
from app.soluciones import assemble, unscored
from app.routers.ia import AIRequest, PreviousContext, _recommend_workflow

ROWS=json.loads((Path(__file__).resolve().parents[2]/'docs/software/catalogo_2026-10-21.json').read_text(encoding='utf-8'))


class SolucionesTests(unittest.TestCase):
    def equipment(self, ident='X1', brand='SingularXYZ', category='GNSS'):
        return unscored({'id_equipo':ident,'marca':brand,'modelo':ident,'categoria':category})

    def test_office_software_unknown_is_not_false_or_pass(self):
        result=rank(ROWS,{'ajuste_red':True})['resultados']
        self.assertEqual(result[0]['software']['nombre'],'PProcessing')
        studio=next(r for r in result if r['software']['marca']=='Emlid')
        self.assertEqual(studio['sin_datos'],1)
        self.assertEqual(studio['porcentaje'],0)
        self.assertEqual(studio['incumplimientos'],0)

    def test_same_brand_does_not_grant_technical_points(self):
        results=rank(ROWS,{'ajuste_red':True},'Emlid')['resultados']
        self.assertEqual(results[0]['software']['nombre'],'PProcessing')

    def test_singular_always_gets_native_software_without_claiming_license(self):
        result=assemble([self.equipment()], [self.equipment('SC260',category='Controladora')], ROWS,{}, {})
        option=result['opciones'][0]
        self.assertEqual(option['software']['software']['nombre'],'PProcessing')
        self.assertIsNone(option['porcentaje'])
        self.assertEqual(option['estado'],'pendiente_validacion')

    def test_emlid_does_not_invent_an_emlid_controller(self):
        result=assemble([self.equipment('RS3','Emlid')], [self.equipment('SC260',category='Controladora')],ROWS,{}, {}, strict=True)
        option=result['opciones'][0]
        self.assertIsNone(option['controladora'])
        self.assertEqual(option['software']['software']['nombre'],'Emlid Studio')
        self.assertEqual(option['estado'],'no_cumple')

    def test_controller_failure_affects_complete_proposal(self):
        ctrl=self.equipment('SC260',category='Controladora')
        ctrl.update(porcentaje=0,detalle=[{'estado':'no_cumple'}])
        result=assemble([self.equipment()], [ctrl],ROWS,{'controladora':{'ram_gb':99}}, {})
        self.assertEqual(result['opciones'][0]['estado'],'no_cumple')
        self.assertEqual(result['opciones'][0]['incumplimientos'],1)

    def test_every_component_is_retained_and_corrected_on_follow_up(self):
        result=ia.normalize_components({'controladora':{'autonomia_h':13},'software':{'gratuito':False}},
            {'gnss':{'canales_min':220},'controladora':{'ram_gb':4},'software':{'gratuito':True,'estatico':True}},[])
        self.assertEqual(result['gnss']['canales_min'],220)
        self.assertEqual(result['controladora'],{'ram_gb':4,'autonomia_h':13})
        self.assertEqual(result['software'],{'estatico':True})

    def test_untrusted_context_has_no_internal_scoring_parameters(self):
        result=ia.normalize_components({'gnss':{'top_n':100,'solo_cotecmi':False,'canales_min':220}}, {}, [])
        self.assertNotIn('top_n',result['gnss'])
        self.assertNotIn('solo_cotecmi',result['gnss'])

    def test_three_family_provider_output_is_validated_once(self):
        raw={'tipo_equipo':'kit','requisitos':{},'componentes':{'gnss':{'canales_min':220},'controladora':{'ram_gb':4},'software':{'estatico':True}},'selecciones':{},'preguntas':[],'omitidos':[]}
        with patch.object(ia,'quota_until',return_value=None), patch.object(ia,'_post_gemini',return_value=(raw,{})):
            parsed=ia.interpret('GNSS, controladora 4 GB y software estático')
        self.assertEqual(set(parsed['componentes']),{'gnss','controladora','software'})
        self.assertTrue(parsed['tiene_criterios'])

    def test_single_family_can_use_component_fields_without_losing_them(self):
        raw={'tipo_equipo':'software','requisitos':{},'componentes':{'software':{'estatico':True}},'preguntas':[],'omitidos':[]}
        with patch.object(ia,'quota_until',return_value=None), patch.object(ia,'_post_gemini',return_value=(raw,{})):
            result=ia.interpret('Software para estatico')
        self.assertEqual(result['requisitos'],{'estatico':True})
        self.assertTrue(result['tiene_criterios'])

    def test_forbidden_selection_cannot_bypass_catalog_scope(self):
        parsed={'componentes':{},'selecciones':{'gnss':'EXTERNO'},'tipo_equipo':'kit','misma_marca':False}
        with self.assertRaises(ValueError):
            _recommend_workflow(parsed,AIRequest(mensaje='Elijo externo',solo_cotecmi=True),[])

    def test_follow_up_software_keeps_previous_receiver(self):
        gnss=self.equipment()
        controller=self.equipment('SC260',category='Controladora')
        previous=PreviousContext(tipo_equipo='gnss',requisitos={'canales_min':220},componentes={'gnss':{'canales_min':220}},referencia_gnss='X1')
        body=AIRequest(mensaje='Ahora software para estático',contexto_previo=previous)
        parsed={'componentes':{'gnss':{'canales_min':220},'software':{'estatico':True}},'selecciones':{},'tipo_equipo':'software','misma_marca':False,'requisitos':{'estatico':True},'respuesta_general':'','omitidos':[]}
        with patch('app.routers.ia.recommend_gnss',return_value={'resultados':[gnss]}), patch('app.routers.ia.software_catalog',return_value=ROWS):
            result=_recommend_workflow(parsed,body,[gnss['equipo'],controller['equipo']])
        self.assertEqual(result['solucion']['opciones'][0]['software']['software']['nombre'],'PProcessing')
        self.assertEqual(result['contexto']['referencia_gnss'],'X1')
