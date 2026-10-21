"""Regresiones: preguntas tras una licitación y costos reservados al servidor."""
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.ia import build_prompt, es_dialogo
from app.routers.ia import AIRequest, PreviousContext, _recommend_workflow
from app.routers.recomendar import ordenar_resultados


class DialogoPreciosTests(unittest.TestCase):
    def previous(self):
        return PreviousContext(tipo_equipo='kit', componentes={
            'gnss':{'canales_min':220}, 'software':{'rinex_2':True}},
            selecciones={'gnss':'JUPITER'}, referencia_gnss='JUPITER')

    def parsed(self, kind='controladora', intention='explicacion'):
        return {'tipo_equipo':kind,'intencion':intention,'requisitos':{},
                'componentes':{'gnss':{'canales_min':220}},'selecciones':{},
                'misma_marca':False,'respuesta_general':'La R80 era provisional; compara pantalla y autonomía con R60.',
                'omitidos':[],'resumen':'Comparación R80/R60','preguntas':[]}

    def test_controller_explanation_keeps_context_without_rebuilding_kit(self):
        previous=self.previous()
        body=AIRequest(mensaje='Por qué R80 y no R60? Cuál es mejor?', contexto_previo=previous)
        with patch('app.routers.ia.recommend_gnss') as ranking, patch('app.routers.ia.assemble') as assemble:
            result=_recommend_workflow(self.parsed(),body,[])
        ranking.assert_not_called()
        assemble.assert_not_called()
        self.assertEqual(result['respuesta'],self.parsed()['respuesta_general'])
        self.assertEqual(result['contexto'],previous.model_dump())
        self.assertIsNone(result['ranking'])
        self.assertEqual(result['solucion']['opciones'],[])

    def test_specific_question_after_software_is_not_a_ranking(self):
        parsed=self.parsed('gnss','consulta_catalogo')
        result=_recommend_workflow(parsed,AIRequest(mensaje='Cuántos GB tiene Jupiter?'),[])
        self.assertEqual(result['modo_respuesta'],'conversacion')
        self.assertEqual(result['rankings'],{})

    def test_current_question_wins_even_if_provider_defaults_to_recommendation(self):
        self.assertTrue(es_dialogo('porque controladora R80 y no una R60?', 'recomendacion'))
        self.assertTrue(es_dialogo('Compara H1 y H2 para interiores', 'comparacion'))
        self.assertFalse(es_dialogo('Haz un ranking de R60 y R80', 'comparacion'))
        self.assertFalse(es_dialogo('Lista todos los GNSS con USB-C', 'consulta_catalogo'))

    def test_public_response_is_natural_and_preserves_tender_context(self):
        parsed=self.parsed()
        parsed['omitidos']=['Condición pendiente de la licitación anterior']
        with patch('app.routers.ia._catalog',return_value=[]), patch('app.routers.ia.interpret',return_value=parsed), TestClient(app) as client:
            response=client.post('/api/ia/recomendar',json={
                'mensaje':'Por qué R80 y no R60?', 'contexto_previo':self.previous().model_dump()})
        self.assertEqual(response.status_code,200)
        data=response.json()
        self.assertEqual(data['respuesta'],parsed['respuesta_general'])
        self.assertEqual(data['requisitos'],{})
        self.assertEqual(data['omitidos'],[])
        self.assertEqual(data['contexto']['referencia_gnss'],'JUPITER')

    def test_comparable_cost_precedes_brand_only_in_technical_ties(self):
        def row(ident,brand,cost,score):
            return {'equipo':{'id_equipo':ident,'marca':brand,
                    'referencia_precio':{'precio_usd':cost,'comparable':True}},
                    'porcentaje':score,'sin_datos':0,'cumplimientos':1}
        rows=[row('SINO','SinoGNSS',3000,100), row('X1','SingularXYZ',2000,100),
              row('CHEAP','Emlid',1000,90)]
        ordenar_resultados(rows)
        self.assertEqual([r['equipo']['id_equipo'] for r in rows],['X1','SINO','CHEAP'])
        self.assertEqual(rows[0]['posicion'],rows[1]['posicion'])

    def test_prices_do_not_reach_provider_or_public_json(self):
        secret={'precio_usd':2897.99,'comparable':True,'fuente_url':'https://price.example/internal'}
        prompt=build_prompt('Compara X1', 'auto', None, {}, [{'id_equipo':'X1','referencia_precio':secret}])
        self.assertNotIn('2897.99',prompt)
        self.assertNotIn('price.example',prompt)
        result={'ranking':{'resultados':[{'equipo':{'modelo':'X1','referencia_precio':secret}}]},
                'respuesta':'Opciones ordenadas','contexto':{}}
        with patch('app.routers.ia._catalog',return_value=[]), patch('app.routers.ia.interpret',return_value=self.parsed('gnss','recomendacion')), patch('app.routers.ia._recommend_workflow',return_value=result), TestClient(app) as client:
            response=client.post('/api/ia/recomendar',json={'mensaje':'Lista los GNSS'})
        self.assertEqual(response.status_code,200)
        self.assertNotIn('referencia_precio',response.text)
        self.assertNotIn('2897.99',response.text)
        self.assertNotIn('price.example',response.text)
