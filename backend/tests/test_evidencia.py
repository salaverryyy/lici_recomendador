import unittest
from app.evidencia import etiqueta_sin_valor

class EvidenciaTests(unittest.TestCase):
    def test_old_numeric_evidence_never_replaces_an_unknown_technical_value(self):
        self.assertEqual(etiqueta_sin_valor({'memoria':{'valor_declarado':'32'}},'memoria'),
                         'No publicado / pendiente de confirmar')

    def test_not_applicable_and_commercial_conditions_remain_explicit(self):
        for text in ['No aplica','Depende del kit ofertado','Modo no especificado por separado']:
            self.assertEqual(etiqueta_sin_valor({'x':{'valor_declarado':text}},'x'),text)
