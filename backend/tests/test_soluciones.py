import json
import unittest
from pathlib import Path
from unittest.mock import patch
from app import ia
from app.software import rank, comparison_advice
from app.soluciones import assemble, unscored
from app.routers.ia import AIRequest, PreviousContext, _recommend_workflow

ROWS=json.loads((Path(__file__).resolve().parents[2]/'docs/software/catalogo_2026-10-21.json').read_text(encoding='utf-8'))


class SolucionesTests(unittest.TestCase):
    def equipment(self, ident='X1', brand='SingularXYZ', category='GNSS'):
        return unscored({'id_equipo':ident,'marca':brand,'modelo':ident,'categoria':category})

    def test_office_software_unknown_is_not_false_or_pass(self):
        result=rank(ROWS,{'ajuste_red':True})['resultados']
        self.assertEqual({r['software']['nombre'] for r in result if r['porcentaje']==100}, {'Compass Solution','PProcessing'})
        studio=next(r for r in result if r['software']['marca']=='Emlid')
        self.assertEqual(studio['sin_datos'],1)
        self.assertEqual(studio['porcentaje'],0)
        self.assertEqual(studio['incumplimientos'],0)

    def test_same_brand_does_not_grant_technical_points(self):
        results=rank(ROWS,{'ajuste_red':True},'Emlid')['resultados']
        self.assertEqual(results[0]['porcentaje'],100)
        self.assertNotEqual(results[0]['software']['marca'],'Emlid')

    def test_common_documented_functions_do_not_pick_universal_winner(self):
        answer = comparison_advice('Cuál es el software más completo', ROWS, {})
        self.assertIn('No hay un ganador universal', answer)
        self.assertIn('Compass Solution y PProcessing', answer)
        self.assertIn('RINEX 2.x', answer)
        self.assertIsNone(comparison_advice('Funciona en macOS?', ROWS, {}))

    def test_copy_claim_is_not_used_as_technical_evidence(self):
        answer = comparison_advice('PProcessing es la copia?', ROWS, {}, 'SinoGNSS')
        self.assertIn('prioriza **Compass Solution**', answer)
        self.assertIn('no acreditan la afirmación', answer)

    def test_unfounded_provider_winner_is_replaced(self):
        parsed={'componentes':{},'selecciones':{},'tipo_equipo':'software','misma_marca':False,'requisitos':{},'respuesta_general':'PProcessing es el mejor por ser moderno','omitidos':[]}
        with patch('app.routers.ia.software_catalog',return_value=ROWS):
            result=_recommend_workflow(parsed,AIRequest(mensaje='Cuál es el software más completo'),[])
        self.assertNotIn('por ser moderno',result['respuesta'])
        self.assertIn('No hay un ganador universal',result['respuesta'])

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
        self.assertIn('Emlid Flow',option['app_campo']['nombre'])
        self.assertEqual(option['estado'],'pendiente_validacion')

    def test_brand_policy_does_not_choose_better_scoring_foreign_controller(self):
        native=self.equipment('R80','SinoGNSS','Controladora')
        native.update(porcentaje=0,detalle=[{'estado':'no_cumple'}])
        foreign=self.equipment('SC260',category='Controladora')
        foreign.update(porcentaje=100)
        option=assemble([self.equipment('Jupiter','SinoGNSS')],[foreign,native],ROWS,{}, {})['opciones'][0]
        self.assertEqual(option['controladora']['equipo']['modelo'],'R80')
        self.assertEqual(option['alternativas_controladora'],[])

    def test_phone_does_not_satisfy_dedicated_controller_requirements(self):
        option=assemble([self.equipment('RS3','Emlid')],[],ROWS,{'controladora':{'ram_gb':8}}, {})['opciones'][0]
        self.assertEqual(option['estado'],'no_cumple')

    def test_missing_required_controller_counts_in_partial_kit_score(self):
        receiver=self.equipment('RS3','Emlid')
        receiver.update(porcentaje=100,detalle=[{'estado':'cumple'}])
        option=assemble([receiver],[],ROWS,{'controladora':{'ram_gb':8},'software':{'estatico':True}}, {})['opciones'][0]
        self.assertEqual(option['porcentaje'],66.67)
        self.assertEqual(option['incumplimientos'],1)

    def test_gnss_list_after_software_does_not_assemble_unsolicited_kit(self):
        gnss=self.equipment()
        gnss.update(porcentaje=100,detalle=[{'clave':'usb_c','estado':'cumple'}])
        parsed={'componentes':{'gnss':{'usb_c':True},'software':{'estatico':True}},'selecciones':{},'tipo_equipo':'gnss','misma_marca':False,'requisitos':{'usb_c':True},'respuesta_general':'','omitidos':[]}
        body=AIRequest(mensaje='Lista de todos los GNSS con USB C',contexto_previo=PreviousContext(tipo_equipo='software',requisitos={'estatico':True}))
        with patch('app.routers.ia.recommend_gnss',return_value={'resultados':[gnss]}), patch('app.routers.ia.software_catalog',return_value=ROWS):
            result=_recommend_workflow(parsed,body,[gnss['equipo']])
        self.assertEqual(result['solucion']['opciones'],[])
        self.assertEqual(len(result['ranking']['resultados']),1)
        self.assertNotIn('Propuesta en orden',result['respuesta'])

    def test_usb_list_excludes_absent_and_unverified_ports(self):
        results=[]
        for ident,state in [('USB','cumple'),('LEMO','no_cumple'),('UNKNOWN','sin_datos')]:
            row=self.equipment(ident)
            row.update(porcentaje=100 if state=='cumple' else 0,detalle=[{'clave':'usb_c','estado':state}])
            results.append(row)
        parsed={'componentes':{'gnss':{'usb_c':True}},'selecciones':{},'tipo_equipo':'gnss','misma_marca':False,'requisitos':{'usb_c':True},'respuesta_general':'','omitidos':[]}
        with patch('app.routers.ia.recommend_gnss',return_value={'resultados':results}), patch('app.routers.ia.software_catalog',return_value=ROWS):
            result=_recommend_workflow(parsed,AIRequest(mensaje='Lista de todos los GNSS con USB C'),[r['equipo'] for r in results])
        self.assertEqual([r['equipo']['id_equipo'] for r in result['ranking']['resultados']],['USB'])
        self.assertIn('1 modelos que cumplen USB-C',result['respuesta'])

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
