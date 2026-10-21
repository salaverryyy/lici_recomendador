import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.soluciones import unscored


class GNSSSelectionTests(unittest.TestCase):
    def test_click_selects_receiver_and_rebuilds_native_kit_without_gemini(self):
        receiver={'id_equipo':'X1','marca':'SingularXYZ','modelo':'X1','categoria':'GNSS'}
        controller={'id_equipo':'SC260','marca':'SingularXYZ','modelo':'SC260','categoria':'Controladora'}
        office={'id_equipo':'PP','id_software':'PP','marca':'SingularXYZ','modelo':'PProcessing',
                'nombre':'PProcessing','categoria':'Software de procesamiento','funciones':{}}
        catalog=[receiver,controller,office,{'id_equipo':'R80','marca':'SinoGNSS','categoria':'Controladora'}]
        ranking=unscored(receiver)
        ranking.update(porcentaje=100,detalle=[{'clave':'usb_c','estado':'cumple'}])
        context={'tipo_equipo':'gnss','requisitos':{'usb_c':True},'componentes':{'gnss':{'usb_c':True}},
                 'selecciones':{'controladora':'R80'},'referencia_gnss':'OLD'}
        with patch('app.routers.ia._catalog',return_value=catalog), \
             patch('app.routers.ia.software_catalog',return_value=[office]), \
             patch('app.routers.ia.recommend_gnss',return_value={'resultados':[ranking]}), \
             patch('app.routers.ia.interpret') as provider, TestClient(app) as client:
            response=client.post('/api/ia/seleccionar-gnss',json={'id_gnss':'X1','contexto_previo':context,'omitidos':['Verificar licencia incluida']})
        self.assertEqual(response.status_code,200,response.text)
        provider.assert_not_called()
        data=response.json()
        self.assertEqual(data['contexto']['selecciones'],{'gnss':'X1'})
        self.assertEqual(data['contexto']['referencia_gnss'],'X1')
        self.assertIn('Verificar licencia incluida',data['omitidos'])
        option=data['solucion']['opciones'][0]
        self.assertEqual(option['controladora']['equipo']['id_equipo'],'SC260')
        self.assertEqual(option['software']['software']['id_software'],'PP')
        self.assertTrue(option['seleccion_explicita'])
        self.assertNotIn('referencia_precio',response.text)

    def test_selection_cannot_bypass_catalog_scope(self):
        with patch('app.routers.ia._catalog',return_value=[]), TestClient(app) as client:
            response=client.post('/api/ia/seleccionar-gnss',json={
                'id_gnss':'EXTERNO','solo_cotecmi':True,'contexto_previo':{'tipo_equipo':'gnss'}})
        self.assertEqual(response.status_code,422)

    def test_selection_does_not_accept_scoring_controls_in_context(self):
        receiver={'id_equipo':'X1','marca':'SingularXYZ','modelo':'X1','categoria':'GNSS'}
        with patch('app.routers.ia._catalog',return_value=[receiver]), TestClient(app) as client:
            response=client.post('/api/ia/seleccionar-gnss',json={
                'id_gnss':'X1','contexto_previo':{'tipo_equipo':'gnss','componentes':{'gnss':{'top_n':100,'solo_cotecmi':False}}}})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()['contexto']['componentes'].get('gnss'),{})
