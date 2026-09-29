import os
import unittest
from unittest.mock import patch

from app import ia
from app.routers.ia import AIRequest, _retrieve_catalog
from pydantic import ValidationError


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

    def test_conversation_history_is_included_in_provider_prompt(self):
        provider = ({
            'tipo_equipo': 'gnss', 'intencion': 'comparacion',
            'requisitos': {}, 'resumen': 'Continúa la comparación.',
            'respuesta_general': 'El segundo era el X1.', 'preguntas': [], 'omitidos': [],
        }, {})
        captured = []

        def fake_provider(prompt):
            captured.append(prompt)
            return provider

        history = [
            {'role': 'user', 'text': 'Compara Jupiter y X1'},
            {'role': 'assistant', 'text': 'Jupiter tiene láser; X1 es un RTK convencional.'},
        ]
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test'}, clear=False), \
             patch.object(ia, 'quota_until', return_value=None), \
             patch.object(ia, '_post_gemini', side_effect=fake_provider):
            ia.interpret('¿Y el segundo?', catalog_context=[], conversation_history=history)
        self.assertIn('Compara Jupiter y X1', captured[0])
        self.assertIn('¿Y el segundo?', captured[0])

    def test_history_size_is_bounded(self):
        with self.assertRaises(ValidationError):
            AIRequest(
                mensaje='Continúa',
                historial=[{'role': 'user', 'text': 'x' * 2500}] * 6,
            )

    def test_rag_prioritizes_explicit_model(self):
        catalog = [
            {'id_equipo': 'A', 'marca': 'Emlid', 'modelo': 'Reach RS3', 'tiene_imu': True},
            {'id_equipo': 'B', 'marca': 'SinoGNSS', 'modelo': 'Jupiter Laser RTK', 'laser': True},
            {'id_equipo': 'C', 'marca': 'SingularXYZ', 'modelo': 'X1', 'tiene_imu': True},
        ]
        retrieved = _retrieve_catalog(catalog, '¿Qué diferencia tiene el Jupiter?', limit=2)
        self.assertEqual(retrieved[0]['id_equipo'], 'B')


if __name__ == '__main__':
    unittest.main()
