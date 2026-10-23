"""Comprueba cobertura real en PostgreSQL, fichas, comparación y contexto de IA."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from fastapi.testclient import TestClient
from app.main import app
from app.routers.ia import _catalog


def main():
    with TestClient(app) as client:
        response=client.get('/api/equipos');response.raise_for_status()
        catalog=response.json()
        missing=[]
        for row in catalog:
            ident=row['id_equipo']
            response=client.get('/api/equipos/'+ident);response.raise_for_status()
            detail=response.json()
            category=row['categoria']
            data=detail['controladora'] if category=='Controladora' else detail['slam'] if category=='Escáner SLAM' else detail['evaluacion']
            prefix='controladora_' if category=='Controladora' else 'slam_' if category=='Escáner SLAM' else ''
            weight='peso_g' if category=='Controladora' else 'peso_operativo_g' if category=='Escáner SLAM' else 'peso_max'
            for field in ('dimensiones_declaradas','peso_condiciones','fisica_fuente'):
                assert data[field] and prefix+field in detail['auditoria'],(ident,field)
            if data[weight] is None:missing.append(ident)
            else:assert data[weight]>0,ident
            if category!='Escáner SLAM':
                assert all(data[k]>0 for k in ('largo_mm','ancho_mm','alto_mm')),ident
            fields=','.join(prefix+k for k in (weight,'dimensiones_declaradas','peso_condiciones'))
            response=client.get('/api/comparar',params={'ids':ident,'columnas':fields});response.raise_for_status()
            assert len(response.json()['columnas'])==3,ident
        assert missing==['SINGULARXYZ-SC260'],missing
        # Verifica que Lici reciba las mismas condiciones que la ficha pública.
        ai=_catalog(False,'auto')
        for row in ai:
            if row.get('categoria')=='Software de procesamiento':continue
            assert row.get('dimensiones_declaradas') and row.get('peso_condiciones'),row['id_equipo']
        print(f'OK: {len(catalog)} fichas y comparaciones; contexto IA con condiciones físicas. Único peso pendiente: SC260.')


if __name__=='__main__':main()
