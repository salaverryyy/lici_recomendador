"""Prueba HTTP de solo lectura con BD real e IA simulada; no consume cuota."""
import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from fastapi.testclient import TestClient
from app.main import app


def main():
    with TestClient(app) as client, patch('app.ia.quota_until',return_value=None):
        response=client.get('/api/software'); response.raise_for_status()
        assert len(response.json()['software'])==3
        context=None
        for kind, requirements, message, selections in (
            ('gnss',{'canales_min':220,'usb_c':True},'Elijo el X1, al menos 220 canales y USB-C',{'gnss':'GNSS-SINGULARXYZ-X1'}),
            ('controladora',{'ram_gb':4},'Ahora la controladora, 4 GB de RAM',{}),
            ('software',{'estatico':True,'ajuste_red':True},'Ahora software estático con ajuste de redes',{}),
        ):
            raw={'tipo_equipo':kind,'requisitos':requirements,'selecciones':selections,'preguntas':[],'omitidos':[]}
            with patch('app.ia._post_gemini',return_value=(raw,{})):
                response=client.post('/api/ia/recomendar',json={'mensaje':message,'contexto_previo':context})
            response.raise_for_status()
            data=response.json(); assert data['estado']=='ok',data
            context=data['contexto']
            first=data['solucion']['opciones'][0]
            assert first['gnss']['equipo']['id_equipo']=='GNSS-SINGULARXYZ-X1'
            assert first['software']['software']['nombre']=='PProcessing'
        assert set(context['componentes'])=={'gnss','controladora','software'}
        assert first['controladora']['detalle'][0]['clave']=='ram_gb'
        assert any(d['clave']=='ajuste_red' for d in first['software']['detalle'])
        raw={'tipo_equipo':'kit','requisitos':{},'componentes':context['componentes'],'selecciones':{'gnss':'GNSS-SINOGNSS-JUPITER'},'preguntas':[],'omitidos':[]}
        with patch('app.ia._post_gemini',return_value=(raw,{})):
            response=client.post('/api/ia/recomendar',json={'mensaje':'GNSS USB-C 220 canales, controladora 4 GB y software con ajuste de redes. Elijo Jupiter.'})
        response.raise_for_status(); data=response.json(); assert data['estado']=='ok',data
        first=data['solucion']['opciones'][0]
        assert first['software']['software']['nombre']=='Compass Solution'
        assert first['software']['sin_datos']>=1, 'No atribuir ajuste de redes sin evidencia'
        assert data['contexto']['selecciones']['gnss']=='GNSS-SINOGNSS-JUPITER'
        print('OK: tres softwares HTTP, secuencia GNSS/controladora/software y consulta conjunta; sin consumo de IA.')


if __name__=='__main__':
    main()
