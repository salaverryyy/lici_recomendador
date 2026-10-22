import unittest
from app.termica import respuesta_termica
from app.recomendador import Preferencias,CRITERIOS,criterios_seleccionados,evaluar_equipo


def evaluate(data,**requirements):
    p=Preferencias(**requirements)
    return evaluar_equipo(p,criterios_seleccionados(p),{c.clave:c.peso for c in CRITERIOS},data,[])


class ThermalComponentTests(unittest.TestCase):
    def setUp(self):
        self.receiver={'categoria':'GNSS','marca':'Marca de prueba','modelo':'Ejemplo A1',
            'temperatura_operacion_min_c':-40,'temperatura_operacion_max_c':65,
            'temperatura_laser_min_c':-20,'temperatura_laser_max_c':50,
            'temperatura_camara_min_c':None,'temperatura_camara_max_c':None,
            'tiene_camara':True,'cantidad_camaras':2,'laser':True}

    def test_camera_does_not_inherit_laser_temperature(self):
        result=evaluate(self.receiver,temperatura_operacion_min_c=-30,temperatura_operacion_max_c=65,necesita_camara=True)
        thermal=[d for d in result['detalle'] if d['unidad']=='°C']
        self.assertTrue(all(d['estado']=='cumple' for d in thermal))
        self.assertEqual([d['valor_equipo'] for d in thermal],[-40,65])
        self.assertTrue(all('no se aplica' in d['observacion'] for d in thermal))

    def test_laser_restriction_only_when_laser_required(self):
        result=evaluate(self.receiver,temperatura_operacion_min_c=-30,temperatura_operacion_max_c=65,laser=True)
        thermal=[d for d in result['detalle'] if d['unidad']=='°C']
        self.assertEqual([d['valor_equipo'] for d in thermal],[-20,50])
        self.assertTrue(all(d['estado']=='incumple' for d in thermal))

    def test_genuine_camera_restriction_is_preserved(self):
        data={**self.receiver,'temperatura_camara_min_c':-30,'temperatura_camara_max_c':50}
        result=evaluate(data,temperatura_operacion_min_c=-30,temperatura_operacion_max_c=65,necesita_camara=True)
        thermal=[d for d in result['detalle'] if d['unidad']=='°C']
        self.assertEqual([d['estado'] for d in thermal],['cumple','incumple'])

    def test_a_component_range_does_not_fill_unknown_receiver_temperature(self):
        result=evaluate({'temperatura_camara_min_c':-30},temperatura_operacion_min_c=-25,necesita_camara=True)
        detail=next(d for d in result['detalle'] if d['unidad']=='°C')
        self.assertEqual(detail['estado'],'sin_datos')

    def test_catalog_answers_show_general_and_specific_ranges(self):
        answer=respuesta_termica('A qué temperatura opera Ejemplo A1?',[self.receiver])
        self.assertIn('-40 a 65',answer)
        self.assertIn('Para el láser',answer)
        self.assertIn('-20 a 50',answer)
        self.assertNotIn('Con cámara',answer)
        followup=respuesta_termica('y el Ejemplo A1?',[self.receiver],[{'role':'user','text':'Qué temperaturas soporta otro equipo?'}])
        self.assertEqual(followup,answer)

    def test_unknown_or_unrelated_question_is_not_replaced(self):
        self.assertIsNone(respuesta_termica('Cuántas cámaras tiene Ejemplo A1?',[self.receiver]))
        self.assertIsNone(respuesta_termica('A cuántos grados se inclina Ejemplo A1?',[self.receiver]))
        self.assertIsNone(respuesta_termica('Qué temperatura soporta Desconocido Q9?',[self.receiver]))

    def test_storage_question_does_not_use_operation_or_laser_bounds(self):
        data={**self.receiver,'temperatura_almacenamiento_min_c':-55,'temperatura_almacenamiento_max_c':85}
        answer=respuesta_termica('Qué temperatura de almacenamiento admite Ejemplo A1?',[data])
        self.assertIn('-55 a 85',answer)
        self.assertIn('en almacenamiento',answer)
        self.assertNotIn('-20 a 50',answer)

    def test_one_camera_does_not_satisfy_double_camera_even_if_thermal_passes(self):
        result=evaluate({**self.receiver,'cantidad_camaras':1},cantidad_camaras_min=2,
                        temperatura_operacion_min_c=-30,temperatura_operacion_max_c=65)
        self.assertEqual(result['incumplimientos'],1)


if __name__=='__main__':unittest.main()
