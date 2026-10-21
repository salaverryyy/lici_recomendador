"""Regresión HTTP con catálogo real; no consume cuota de IA ni modifica la BD."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'backend'))
from fastapi.testclient import TestClient
from app.main import app


def main():
    with TestClient(app) as client:
        response=client.post('/api/recomendar',json={'usb_c':True,'top_n':100})
        response.raise_for_status()
        rows=response.json()['resultados']
        ids=[r['equipo']['id_equipo'] for r in rows]
        assert ids.index('GNSS-EMLID-RS3')<ids.index('GNSS-EMLID-RS2PLUS')
        for minimum in (8,16,32):
            response=client.post('/api/recomendar',json={'memoria_min_gb':minimum,'top_n':100})
            response.raise_for_status()
            rows=response.json()['resultados']
            jupiter=next(r for r in rows if r['equipo']['id_equipo']=='GNSS-SINOGNSS-JUPITER')
            assert jupiter['porcentaje']==100
            assert jupiter['detalle'][0]['requiere_ampliacion']
            assert jupiter['detalle'][0]['memoria_fabrica_gb']==4
        t20=next(r for r in rows if r['equipo']['id_equipo']=='GNSS-SINOGNSS-T20')
        assert t20['porcentaje']==100 and t20['detalle'][0]['tipo_ampliacion']=='opcion_fabrica'
        raw={'tipo_equipo':'gnss','requisitos':{'memoria_min_gb':32},'resumen':'GNSS con 32 GB admitiendo ampliación','preguntas':[],'omitidos':[]}
        with patch('app.ia.quota_until',return_value=None),patch('app.ia._post_gemini',return_value=(raw,{})):
            response=client.post('/api/ia/recomendar',json={'mensaje':'GNSS con 32 GB, puede ser con ampliación'})
        response.raise_for_status()
        data=response.json()
        assert data['estado']=='ok' and not data['solucion']['opciones']
        jupiter=next(r for r in data['ranking']['resultados'] if r['equipo']['id_equipo']=='GNSS-SINOGNSS-JUPITER')
        assert jupiter['porcentaje']==100 and jupiter['detalle'][0]['requiere_ampliacion']
        directory=root/'tmp/orden-memoria'; directory.mkdir(parents=True,exist_ok=True)
        (directory/'chat.json').write_text(json.dumps(data,ensure_ascii=False,default=str),encoding='utf-8')
        response=client.post('/api/recomendar',json={'memoria_min_gb':32,'memoria_solo_fabrica':True,'top_n':100})
        response.raise_for_status()
        strict=response.json()['resultados']
        for ident in ('GNSS-SINOGNSS-JUPITER','GNSS-SINOGNSS-T20'):
            assert next(r for r in strict if r['equipo']['id_equipo']==ident)['porcentaje']==0
        print('OK: RS3 antes de RS2+, Jupiter 4 a 32 GB con puntos completos, T20 opcional y mínimo instalado estricto. Chat y API coherentes.')


if __name__=='__main__':
    main()
