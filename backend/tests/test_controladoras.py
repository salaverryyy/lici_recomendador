import unittest
from decimal import Decimal
from fastapi import HTTPException
from app.controladoras import evaluate, validate, available_options

class ControllerTests(unittest.TestCase):
    def test_equivalent_options_are_deduplicated_and_match(self):
        rows = [{'sistema_operativo':'Android OS','proteccion_ip':'ip 67','bluetooth_version':'Bluetooth v5.0'},
                {'sistema_operativo':' Android ','proteccion_ip':'IP67','bluetooth_version':'5'}]
        options = {c['clave']:c['opciones'] for c in available_options(rows)}
        self.assertEqual(options['sistema_operativo'], ['Android'])
        self.assertEqual(options['proteccion_ip'], ['IP67'])
        self.assertEqual(options['bluetooth_version'], ['5.0'])
        self.assertEqual(evaluate(rows[0], {'sistema_operativo':'Android','proteccion_ip':'IP67','bluetooth_version':'5.0'})['porcentaje'],100)

    def test_database_numbers_can_be_validated_for_partial_edits(self):
        validate({'ram_gb':Decimal('4'), 'temperatura_operacion_min_c':Decimal('-20')})

    def test_tender_threshold_can_exceed_every_catalogue_screen(self):
        rows = [{'pantalla_pulgadas':5.45}, {'pantalla_pulgadas':5.5}]
        options = {c['clave']:c['opciones'] for c in available_options(rows)}
        self.assertIn(6, options['pantalla_pulgadas'])
        for row in rows:
            self.assertEqual(evaluate(row, {'pantalla_pulgadas':6})['porcentaje'],0)

    def test_unknown_stays_unknown_and_no_is_ignored(self):
        result=evaluate({'ram_gb':4},{'ram_gb':4,'wifi':True,'nfc':False})
        self.assertEqual(result['porcentaje'],50)
        self.assertEqual(result['sin_datos'],1)
        self.assertEqual(len(result['detalle']),2)

    def test_temperature_and_maximum_weight(self):
        result=evaluate({'temperatura_operacion_min_c':-20,'peso_g':412},
                        {'temperatura_operacion_min_c':-30,'peso_g':450})
        self.assertEqual(result['porcentaje'],50)

    def test_ip68_does_not_imply_ip67(self):
        self.assertEqual(evaluate({'proteccion_ip':'IP68'},{'proteccion_ip':'IP67'})['porcentaje'],0)

    def test_invalid_and_non_finite_inputs(self):
        for values in ({'ram_gb':-1},{'ram_gb':float('inf')},{'unknown':3},{'wifi':'true'}):
            with self.assertRaises(HTTPException):validate(values)

    def test_operating_range(self):
        with self.assertRaises(HTTPException):
            validate({'temperatura_operacion_min_c':40,'temperatura_operacion_max_c':20})
