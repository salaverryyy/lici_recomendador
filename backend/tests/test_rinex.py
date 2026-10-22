import unittest

from app.recomendador import CRITERIOS, Preferencias, criterios_seleccionados, evaluar_equipo
from app.rinex import capacidad_rinex


def evaluate(data, **preferences):
    pref = Preferencias(**preferences)
    return evaluar_equipo(pref, criterios_seleccionados(pref),
                          {c.clave: c.peso for c in CRITERIOS}, data, [])


class RinexTests(unittest.TestCase):
    def test_conversion_covers_export_with_visible_condition(self):
        result = evaluate({'rinex_3_conversion': True,
                           'rinex_conversion_software': 'CRU'}, registro_rinex_3=True)
        self.assertEqual(result['porcentaje'], 100)
        detail = result['detalle'][0]
        self.assertTrue(detail['requiere_conversion'])
        self.assertEqual(detail['software_conversion'], 'CRU')
        self.assertIn('no se presume software incluido', detail['observacion'])

    def test_conversion_does_not_prove_native_recording(self):
        for native, expected in ((None, 'sin_datos'), (False, 'incumple')):
            result = evaluate({'rinex_3_directo': native, 'rinex_3_conversion': True},
                              registro_rinex_3=True, rinex_3_nativo=True)
            self.assertEqual(result['porcentaje'], 0)
            self.assertEqual(result['detalle'][0]['estado'], expected)

    def test_direct_recording_satisfies_native_and_export(self):
        for native in (False, True):
            result = evaluate({'rinex_3_directo': True, 'rinex_3_conversion': True},
                              registro_rinex_3=True, rinex_3_nativo=native)
            self.assertEqual(result['porcentaje'], 100)
            self.assertFalse(result['detalle'][0]['requiere_conversion'])

    def test_legacy_compatibility_does_not_prove_native(self):
        data = {'registro_rinex_3': True}
        self.assertEqual(evaluate(data, registro_rinex_3=True)['porcentaje'], 100)
        strict = evaluate(data, registro_rinex_3=True, rinex_3_nativo=True)
        self.assertEqual(strict['sin_datos'], 1)

    def test_input_support_is_not_receiver_export(self):
        result = evaluate({'rinex_conversion_software': 'Office', 'importa_rinex': True},
                          registro_rinex_3=True)
        self.assertEqual(result['sin_datos'], 1)

    def test_version_families_are_evaluated_separately(self):
        result = evaluate({'rinex_3_directo': True},
                          registro_rinex_3=True, registro_rinex_2=True)
        self.assertEqual(result['porcentaje'], 50)
        self.assertEqual(result['sin_datos'], 1)

    def test_exact_revision_is_preserved_in_evidence(self):
        value, conditional, note = capacidad_rinex({
            'rinex_3_directo': True,
            'rinex_conversion_nota': 'Directo 3.02; no acredita otras revisiones nativas.'}, '3')
        self.assertTrue(value)
        self.assertFalse(conditional)
        self.assertIn('no acredita otras revisiones nativas', note)


if __name__ == '__main__':
    unittest.main()
