"""Copia privada de PostgreSQL para migración; ejecutar con el Python del backend."""
import os
from pathlib import Path
import shutil
import subprocess
from datetime import datetime
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def main():
    load_dotenv(ROOT / 'backend' / '.env')
    binary = shutil.which('pg_dump')
    if not binary:
        candidatos = sorted(Path('C:/Program Files/PostgreSQL').glob('*/bin/pg_dump.exe'))
        binary = str(candidatos[-1]) if candidatos else None
    if not binary:
        raise SystemExit('No se encontró pg_dump. Usa Backup de pgAdmin o añade PostgreSQL/bin a PATH.')
    carpeta = ROOT / 'backups'
    carpeta.mkdir(exist_ok=True)
    salida = carpeta / ('licitex_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.dump')
    entorno = os.environ.copy()
    if os.getenv('DATABASE_URL'):
        entorno['PGDATABASE'] = os.environ['DATABASE_URL']
    else:
        for destino, origen, default in [
            ('PGHOST', 'DB_HOST', 'localhost'), ('PGPORT', 'DB_PORT', '5432'),
            ('PGDATABASE', 'DB_NAME', 'interfaz_lici'), ('PGUSER', 'DB_USER', 'postgres'),
            ('PGPASSWORD', 'DB_PASSWORD', ''),
        ]:
            entorno[destino] = os.getenv(origen, default)
    args = [binary, '--format=custom', '--no-owner', '--no-acl', '--no-password',
            '--file', str(salida)]
    # Conservar esquema, pero no transportar sesiones ni enlaces de recuperación.
    for tabla in ['admin_sessions', 'admin_login_attempts',
                  'admin_password_reset_tokens', 'admin_email_verification_tokens']:
        args += ['--exclude-table-data=public.' + tabla]
    resultado = subprocess.run(args, env=entorno, capture_output=True)
    if resultado.returncode:
        raise SystemExit('Falló el respaldo. Verifica conexión y versión de pg_dump en pgAdmin.')
    restore = str(Path(binary).with_name('pg_restore.exe' if os.name == 'nt' else 'pg_restore'))
    comprobacion = subprocess.run([restore, '--list', str(salida)], capture_output=True)
    if comprobacion.returncode:
        raise SystemExit('No se pudo verificar el índice del respaldo.')
    print('Respaldo creado y su índice verificado:', salida)
    print('Privado: contiene hashes de cuentas. Fotos/PDF se migran por separado.')


if __name__ == '__main__':
    main()
