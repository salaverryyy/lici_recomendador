import unittest
from decimal import Decimal
from fastapi import HTTPException
from app.controladoras import evaluate, validate

class ControllerTests(unittest.TestCase):
    def test_database_numbers_can_be_validated_for_partial_edits(self):
        validate({'ram_gb':Decimal('4'), 'temperatura_operacion_min_c':Decimal('-20')})

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
