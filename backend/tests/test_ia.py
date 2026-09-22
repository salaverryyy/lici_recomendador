import os
import unittest
from unittest.mock import patch

from app import ia


class AITests(unittest.TestCase):
    def test_gnss_output_is_strictly_validated(self):
        provider = ({
            'tipo_equipo': 'gnss',
            'requisitos': {'cantidad_camaras_min': 2, 'laser': True, 'inventado': 7},
            'resumen': 'GNSS visual con láser.',
            'preguntas': [],
            'omitidos': [],
        }, {'promptTokenCount': 100, 'candidatesTokenCount': 20})
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test'}, clear=False), \
             patch.object(ia, 'quota_until', return_value=None), \
             patch.object(ia, '_post_gemini', return_value=provider):
            result = ia.interpret('Quiero doble cámara y láser')
        self.assertEqual(result['tipo_equipo'], 'gnss')
        self.assertEqual(result['requisitos'], {'cantidad_camaras_min': 2, 'laser': True})
        self.assertIn('inventado', result['omitidos'])
        self.assertTrue(result['tiene_criterios'])

    def test_follow_up_merges_previous_controller_requirements(self):
        provider = ({
            'tipo_equipo': 'controladora',
            'requisitos': {'autonomia_h': 12},
            'resumen': 'Controladora robusta.', 'preguntas': [], 'omitidos': [],
        }, {})
        previous = {'ram_gb': 4, 'wifi': True}
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test'}, clear=False), \
             patch.object(ia, 'quota_until', return_value=None), \
             patch.object(ia, '_post_gemini', return_value=provider):
            result = ia.interpret('Además, 12 horas', 'controladora', 'controladora', previous)
        self.assertEqual(result['requisitos'], {'ram_gb': 4, 'wifi': True, 'autonomia_h': 12})

    def test_status_explains_missing_key(self):
        with patch.dict(os.environ, {'AI_PROVIDER': 'gemini', 'GEMINI_API_KEY': ''}, clear=False), \
             patch.object(ia, 'quota_until', return_value=None):
            result = ia.status()
        self.assertFalse(result['disponible'])
        self.assertEqual(result['motivo'], 'configuracion')

    def test_general_catalog_question_can_answer_without_ranking_fields(self):
        provider = ({
            'tipo_equipo': 'gnss', 'intencion': 'consulta_catalogo',
            'requisitos': {}, 'resumen': 'Comparación general.',
            'respuesta_general': 'Jupiter destaca para replanteo con láser; X1 para un flujo RTK convencional.',
            'preguntas': ['¿Necesitas láser?'], 'omitidos': [],
        }, {})
        catalog = [{'marca': 'SinoGNSS', 'modelo': 'Jupiter Laser RTK', 'laser_alcance_m': 50}]
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test'}, clear=False), \
             patch.object(ia, 'quota_until', return_value=None), \
             patch.object(ia, '_post_gemini', return_value=provider):
            result = ia.interpret('¿Cuál es el mejor equipo?', catalog_context=catalog)
        self.assertFalse(result['tiene_criterios'])
        self.assertEqual(result['intencion'], 'consulta_catalogo')
        self.assertIn('Jupiter', result['respuesta_general'])


if __name__ == '__main__':
    unittest.main()
