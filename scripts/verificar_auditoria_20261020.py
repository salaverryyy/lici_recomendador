"""Comprobación de solo lectura: evidencia de cada NULL y comparadores completos."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from fastapi.testclient import TestClient
from app.main import app
from app.routers.comparar import COLUMNAS
from app.controladoras import META as CONTROLLER_META
from app.slam import META as SLAM_META


def main():
    with TestClient(app) as client:
        response = client.get('/api/equipos')
        response.raise_for_status()
        catalog = response.json()
        equipment = catalog['equipos'] if isinstance(catalog, dict) else catalog
        pending = 0
        for equipment_row in equipment:
            ident = equipment_row['id_equipo']
            response = client.get('/api/equipos/' + ident)
            response.raise_for_status()
            detail = response.json()
            category = equipment_row['categoria']
            key, prefix, columns = (
                ('controladora', 'controladora_', ['controladora_'+k for k in CONTROLLER_META])
                if category == 'Controladora' else
                ('slam', 'slam_', ['slam_'+k for k in SLAM_META])
                if category == 'Escáner SLAM' else
                ('evaluacion', '', list(COLUMNAS))
            )
            for field, value in (detail[key] or {}).items():
                if field != 'id_equipo' and value is None:
                    assert prefix+field in detail['auditoria'], (ident, field, 'Sin evidencia')
                    pending += 1
            response = client.get('/api/comparar', params={'ids': ident, 'columnas': ','.join(columns)})
            response.raise_for_status()
            comparison = response.json()
            assert len(comparison['columnas']) == len(columns), ident
            assert all(
                v is not None and v != ''
                for c in comparison['columnas'] for v in c['valores'].values()
            ), ident
        print(f'OK: {len(equipment)} fichas HTTP y comparadores completos; {pending} campos nulos con evidencia.')


if __name__ == '__main__':
    main()
