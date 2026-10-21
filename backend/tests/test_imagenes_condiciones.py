import base64
import json
import os
from io import BytesIO
from unittest import TestCase
from unittest.mock import patch
from PIL import Image
from pydantic import ValidationError
from app.imagenes_ia import ImageInput
from app.routers.ia import AIRequest
from app import ia
from fastapi.testclient import TestClient
from app.main import app
from app.recomendador import Preferencias, CRITERIOS, criterios_seleccionados, evaluar_equipo


def image_input():
    out=BytesIO();Image.new('RGB',(100,100),'white').save(out,format='PNG')
    return ImageInput(nombre='licitacion.png',mime_type='image/png',data=base64.b64encode(out.getvalue()).decode())


def evaluate(p,data):
    return evaluar_equipo(p,criterios_seleccionados(p),{c.clave:c.peso for c in CRITERIOS},data,[])


class ImagesAndConditionsTests(TestCase):
    def test_invalid_image_http_does_not_echo_base64(self):
        value=base64.b64encode(b'private-invalid-image').decode()
        with TestClient(app) as client:
            response=client.post('/api/ia/recomendar',json={'mensaje':'Lee esta pagina','imagenes':[{'nombre':'bad.png','mime_type':'image/png','data':value}]})
        self.assertEqual(response.status_code,422)
        self.assertNotIn(value,response.text)
    def test_fake_file_and_wrong_mime_are_rejected(self):
        with self.assertRaises(ValidationError):ImageInput(nombre='bad.png',mime_type='image/png',data=base64.b64encode(b'not a picture').decode())
        good=image_input()
        with self.assertRaises(ValidationError):ImageInput(nombre='bad.jpg',mime_type='image/jpeg',data=good.data)
        with self.assertRaises(ValidationError):AIRequest(mensaje='lee estas imagenes',imagenes=[good]*4)

    def test_image_is_transmitted_to_gemini_not_only_its_filename(self):
        raw={'tipo_equipo':'gnss','requisitos':{}}
        body={'candidates':[{'content':{'parts':[{'text':json.dumps(raw)}]},'finishReason':'STOP'}]}
        captured=[]
        def post(request,**kwargs):
            captured.append(json.loads(request.data));return BytesIO(json.dumps(body).encode())
        with patch.dict(os.environ,{'GEMINI_API_KEY':'test-key'}),patch.object(ia,'urlopen',side_effect=post):
            ia._post_gemini_model('Lee la imagen','test-model',[image_input()])
        self.assertEqual(captured[0]['contents'][0]['parts'][1]['inlineData']['mimeType'],'image/png')

    def test_uncertainty_is_retained_for_manual_review(self):
        raw={'tipo_equipo':'gnss','requisitos':{},'preguntas':[],'omitidos':[],'lectura_imagenes':[{'indice':1,'texto':'Memoria: cifra poco clara','dudas':['la cifra de memoria podría ser 8 o 16 GB']} ]}
        with patch.object(ia,'quota_until',return_value=None),patch.object(ia,'_post_gemini',return_value=(raw,{})):
            result=ia.interpret('Lee la licitacion',imagenes=[image_input()])
        self.assertTrue(any('Imagen 1' in d for d in result['omitidos']))
        self.assertEqual(result['requisitos'],{})
        self.assertEqual(len(result['lectura_imagenes']),1)

    def test_missing_image_reading_does_not_create_a_ranking(self):
        raw={'tipo_equipo':'gnss','requisitos':{'canales_min':220}}
        with patch.object(ia,'quota_until',return_value=None),patch.object(ia,'_post_gemini',return_value=(raw,{})):
            with self.assertRaises(ia.AIProviderError):ia.interpret('Lee la licitacion',imagenes=[image_input()])

    def test_internal_factory_order_meets_internal_minimum(self):
        data={'memoria':4,'memoria_es_interna':True,'memoria_expandible':True,'memoria_expandida_max_gb':32,'memoria_interna_opcional_max_gb':32}
        result=evaluate(Preferencias(memoria_min_gb=8,memoria_solo_fabrica=True),data)
        self.assertEqual(result['porcentaje'],100)
        self.assertEqual(result['detalle'][0]['tipo_ampliacion'],'opcion_fabrica')
        self.assertEqual(result['detalle'][0]['memoria_fabrica_gb'],4)
        self.assertTrue(result['detalle'][0]['opcion_interna'])

    def test_internal_memory_from_image_preserves_internal_flag_if_provider_omits_it(self):
        raw={'tipo_equipo':'gnss','requisitos':{'memoria_min_gb':8},'preguntas':[],'omitidos':[],'lectura_imagenes':[{'indice':1,'texto':'Memoria interna: mínimo 8 GB','dudas':[]} ]}
        with patch.object(ia,'quota_until',return_value=None),patch.object(ia,'_post_gemini',return_value=(raw,{})):
            result=ia.interpret('Interpreta la captura',imagenes=[image_input()])
        self.assertTrue(result['requisitos']['memoria_solo_fabrica'])
        self.assertTrue(result['componentes']['gnss']['memoria_solo_fabrica'])

    def test_factory_option_is_preferred_over_external_capacity_at_same_maximum(self):
        result=evaluate(Preferencias(memoria_min_gb=8),{'memoria':4,'memoria_expandible':True,'memoria_expandida_max_gb':32,'memoria_opcional_fabrica_max_gb':32})
        self.assertEqual(result['detalle'][0]['tipo_ampliacion'],'opcion_fabrica')

    def test_smallest_documented_factory_configuration_covers_minimum(self):
        data={'memoria':4,'memoria_interna_opcional_max_gb':32,'memoria_interna_opciones_gb':[8,16,32]}
        for minimum,expected in ((8,8),(12,16),(32,32)):
            result=evaluate(Preferencias(memoria_min_gb=minimum,memoria_solo_fabrica=True),data)
            self.assertEqual(result['porcentaje'],100)
            self.assertEqual(result['detalle'][0]['valor_equipo'],expected)

    def test_adapter_gets_full_points_but_cannot_become_native(self):
        data={'usb_c':False,'usb_c_con_adaptador':True}
        result=evaluate(Preferencias(usb_c=True),data)
        self.assertEqual(result['porcentaje'],100)
        self.assertTrue(result['detalle'][0]['requiere_adaptador'])
        self.assertEqual(evaluate(Preferencias(usb_c=True,usb_c_nativo=True),data)['porcentaje'],0)
        self.assertEqual(evaluate(Preferencias(usb_c=True),{'lemo':True,'lemo_pines':7,'usb_c':False})['porcentaje'],0)

    def test_lte_requires_physical_sim_not_phone_or_3g(self):
        p=Preferencias(lte_4g=True)
        self.assertEqual(evaluate(p,{'lte_4g':True,'sim_fisica':True})['porcentaje'],100)
        self.assertEqual(evaluate(p,{'lte_4g':False,'sim_fisica':True})['porcentaje'],0)
        self.assertEqual(evaluate(p,{'lte_4g':True})['sin_datos'],1)
        self.assertEqual(evaluate(p,{'lte_4g':True,'sim_fisica':False})['porcentaje'],0)
