import io
import json
import os
import unittest
from unittest.mock import patch

from app import ia
from app.routers.ia import AIRequest, _answer, _explicit_catalog_type, _mark_shared_error, _retrieve_catalog
from pydantic import ValidationError


class AITests(unittest.TestCase):
    def test_response_error_does_not_write_global_unavailability(self):
        with patch('app.routers.ia.connect') as connect:
            _mark_shared_error(ia.AIProviderError(
                'Respuesta inválida', code=502, reason='respuesta_invalida'
            ))
        connect.assert_not_called()

    def test_perfect_partial_match_is_not_presented_as_full_tender_compliance(self):
        ranking = {'empate_en_primer_puesto': True, 'resultados': [{
            'equipo': {'marca': 'SingularXYZ', 'modelo': 'X1'},
            'porcentaje': 100, 'explicacion': 'Cumple los criterios evaluados.',
        }]}
        answer = _answer('gnss', ranking, ['RTCM/CMR: pendiente de comprobar'])
        self.assertIn('Una de las mejores coincidencias', answer)
        self.assertIn('no acredita el cumplimiento total', answer)

    def test_provider_reads_all_text_parts_and_ignores_thoughts(self):
        data = {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [
            {'thought': True, 'text': 'Razonamiento privado, no es JSON'},
            {'text': '{"tipo_equipo":"gnss",'},
            {'text': '"requisitos":{"canales_min":220}}'},
        ]}}]}
        raw, usage = ia._decode_gemini(data, 'test-model')
        self.assertEqual(raw['requisitos'], {'canales_min': 220})
        self.assertEqual(usage['_model'], 'test-model')

    def test_truncated_json_is_never_used_as_a_partial_ranking(self):
        data = {'candidates': [{'finishReason': 'MAX_TOKENS', 'content': {'parts': [
            {'text': '{"tipo_equipo":"gnss","requisitos":{}}'},
        ]}}]}
        with self.assertRaises(ia.AIProviderError) as caught:
            ia._decode_gemini(data, 'test-model')
        self.assertEqual(caught.exception.reason, 'respuesta_truncada')
        self.assertEqual(caught.exception.code, 502)
        self.assertFalse(caught.exception.quota)
        self.assertFalse(caught.exception.retryable)

    def test_invalid_response_shapes_have_a_specific_error(self):
        for data in ({}, {'candidates': []}, {'candidates': [{'content': {'parts': [
            {'text': '[]'},
        ]}}]}):
            with self.subTest(data=data), self.assertRaises(ia.AIProviderError) as caught:
                ia._decode_gemini(data, 'test-model')
            self.assertEqual(caught.exception.reason, 'respuesta_invalida')

    def test_truncation_retries_with_more_output_budget(self):
        responses = [
            {'candidates': [{'finishReason': 'MAX_TOKENS'}]},
            {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [
                {'text': '{"tipo_equipo":"gnss","requisitos":{"canales_min":220}}'},
            ]}}]},
        ]
        requests = []

        def provider(request, **kwargs):
            requests.append(json.loads(request.data))
            return io.BytesIO(json.dumps(responses.pop(0)).encode())

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test'}), \
             patch.object(ia, 'urlopen', side_effect=provider):
            raw, _ = ia._post_gemini_model('Licitación extensa', 'test-model')
        self.assertEqual(raw['requisitos']['canales_min'], 220)
        self.assertEqual(requests[0]['generationConfig']['maxOutputTokens'], 8192)
        self.assertEqual(requests[1]['generationConfig']['maxOutputTokens'], 16384)
        self.assertIn('responseJsonSchema', requests[0]['generationConfig'])

    def test_invalid_output_can_use_a_model_fallback_without_global_downtime(self):
        result = ({'tipo_equipo': 'gnss', 'requisitos': {}}, {})
        with patch.object(ia, 'model_chain', return_value=['first', 'second']), \
             patch.object(ia, '_post_gemini_model', side_effect=[
                 ia.AIProviderError('Inválida', code=502, reason='respuesta_invalida'), result,
             ]), patch.object(ia, 'mark_quota') as mark_quota:
            response=ia._post_gemini('Consulta')
            self.assertEqual(response[0], result[0])
            self.assertTrue(response[1]['_fallback'])
            self.assertEqual(response[1]['_fallback_reasons'][0]['motivo'],'respuesta_invalida')
        mark_quota.assert_not_called()

    def test_omitted_tender_conditions_are_not_silently_cut_at_twelve(self):
        omitted = [f'Condición contractual {number}' for number in range(18)]
        provider = ({'tipo_equipo': 'gnss', 'requisitos': {'canales_min': 220},
                     'omitidos': omitted}, {})
        with patch.object(ia, 'quota_until', return_value=None), \
             patch.object(ia, '_post_gemini', return_value=provider):
            result = ia.interpret('Licitación con varios requisitos adicionales')
        self.assertEqual(result['omitidos'], omitted)

    def test_model_chain_keeps_order_and_ignores_duplicates(self):
        with patch.dict(
            os.environ,
            {
                'GEMINI_MODEL': 'gemini-principal',
                'GEMINI_FALLBACK_MODELS': 'gemini-respaldo, gemini-principal, gemini-respaldo',
            },
            clear=False,
        ):
            self.assertEqual(
                ia.model_chain(),
                ['gemini-principal', 'gemini-respaldo'],
            )

    def test_quota_error_uses_next_configured_model(self):
        provider_result = ({'tipo_equipo': 'gnss'}, {'_model': 'gemini-respaldo'})
        with patch.dict(
            os.environ,
            {
                'GEMINI_MODEL': 'gemini-principal',
                'GEMINI_FALLBACK_MODELS': 'gemini-respaldo',
            },
            clear=False,
        ), patch.object(
            ia,
            '_post_gemini_model',
            side_effect=[
                ia.AIProviderError(
                    'Cuota agotada', code=429, reason='cuota_agotada', quota=True
                ),
                provider_result,
            ],
        ) as provider:
            result = ia._post_gemini('Consulta técnica')

        self.assertEqual(result[0], provider_result[0])
        self.assertEqual(result[1]['_model'], 'gemini-respaldo')
        self.assertTrue(result[1]['_fallback'])
        self.assertEqual(result[1]['_primary_model'], 'gemini-principal')
        self.assertEqual(result[1]['_fallback_reasons'][0]['codigo'], 429)
        self.assertEqual(
            [call.args[1] for call in provider.call_args_list],
            ['gemini-principal', 'gemini-respaldo'],
        )

    def test_shared_quota_starts_only_after_all_models_are_exhausted(self):
        retry_at = ia.datetime.now(ia.timezone.utc) + ia.timedelta(minutes=5)
        with patch.dict(
            os.environ,
            {
                'GEMINI_MODEL': 'gemini-principal',
                'GEMINI_FALLBACK_MODELS': 'gemini-respaldo',
            },
            clear=False,
        ), patch.object(
            ia,
            '_post_gemini_model',
            side_effect=[
                ia.AIProviderError('Sin cuota', code=429, quota=True),
                ia.AIProviderError('Sin cuota', code=429, quota=True),
            ],
        ), patch.object(ia, 'mark_quota', return_value=retry_at) as mark_quota:
            with self.assertRaises(ia.AIProviderError) as caught:
                ia._post_gemini('Consulta técnica')

        self.assertEqual(caught.exception.code, 429)
        self.assertEqual(caught.exception.retry_at, retry_at)
        mark_quota.assert_called_once_with(None)

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

    def test_explicit_sc260_switches_a_gnss_chat_to_controllers(self):
        catalog = [
            {'marca': 'SingularXYZ', 'modelo': 'SC260', 'categoria': 'Controladora'},
            {'marca': 'SingularXYZ', 'modelo': 'X1', 'categoria': 'GNSS'},
        ]
        self.assertEqual(
            _explicit_catalog_type(catalog, 'Compara la **SingularXYZ SC260**'),
            'controladora',
        )

    def test_slam_requirements_are_validated(self):
        provider = ({
            'tipo_equipo': 'slam',
            'requisitos': {'aplicaciones': 'Minería', 'alcance_lidar_m': 70,
                           'puntos_por_segundo': 200000, 'inventado': True},
            'resumen': 'Escáner SLAM para minería.',
            'preguntas': [], 'omitidos': [],
        }, {})
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test'}, clear=False), \
             patch.object(ia, 'quota_until', return_value=None), \
             patch.object(ia, '_post_gemini', return_value=provider):
            result = ia.interpret('Necesito un SLAM para mina con 70 metros')
        self.assertEqual(result['tipo_equipo'], 'slam')
        self.assertEqual(result['requisitos']['alcance_lidar_m'], 70)
        self.assertIn('inventado', result['omitidos'])


if __name__ == '__main__':
    unittest.main()
