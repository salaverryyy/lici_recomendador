import asyncio
from io import BytesIO
import tempfile
import time
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from pypdf import PdfWriter
from app.routers import admin_almacenamiento as a

class StorageTests(TestCase):
    def test_pdf_with_owner_restrictions_but_no_open_password_is_accepted(self):
        writer=PdfWriter(); writer.add_blank_page(width=100,height=100)
        writer.encrypt(user_password='',owner_password='owner-only')
        out=BytesIO(); writer.write(out)
        self.assertEqual(a.validar_archivo(out.getvalue(),'ficha'),('pdf','application/pdf'))

    def test_pdf_requiring_open_password_is_rejected(self):
        writer=PdfWriter(); writer.add_blank_page(width=100,height=100)
        writer.encrypt(user_password='required')
        out=BytesIO(); writer.write(out)
        with self.assertRaises(HTTPException): a.validar_archivo(out.getvalue(),'ficha')

    session = {'csrf_token':'test-session-secret'}
    def manifest(self, size):
        return {'id':'a'*32,'equipo':'EMLID-RS2','tipo':'ficha','bytes':size,'expira':time.time()+100}

    def test_six_megabyte_pdf_is_assembled_validated_and_registered(self):
        writer=PdfWriter(); writer.add_blank_page(width=100,height=100)
        writer.add_metadata({'/TestPayload':'x'*(6*1024*1024)})
        out=BytesIO(); writer.write(out)
        pdf=out.getvalue()
        manifest=self.manifest(len(pdf)); token=a.firmar(manifest,self.session)
        with tempfile.TemporaryDirectory() as directory, patch.object(a,'UPLOAD_DIR',Path(directory)), patch.object(a,'modo',return_value='local'), patch.object(a,'guardar',return_value=('url','s3:equipos/final.pdf')) as save, patch.object(a,'registrar',return_value={'id':1}) as register:
            for n,offset in enumerate(range(0,len(pdf),a.CHUNK)):
                block=pdf[offset:offset+a.CHUNK]
                class Request:
                    async def stream(self): yield block
                asyncio.run(a.fragmento(n,token,Request(),self.session))
            self.assertEqual(a.finalizar(a.Operacion(token=token),self.session),{'id':1})
            self.assertEqual(save.call_args.args[0],pdf)
            self.assertEqual(save.call_args.args[1:],('pdf','application/pdf'))
            register.assert_called_once()
            self.assertFalse(any(p.is_file() for p in Path(directory).rglob('*')))

    def test_tokens_are_bound_to_session_and_expiry(self):
        manifest=self.manifest(100); token=a.firmar(manifest,self.session)
        with self.assertRaises(HTTPException): a.verificar(token,{'csrf_token':'other'})
        manifest['expira']=time.time()-1
        with self.assertRaises(HTTPException): a.verificar(a.firmar(manifest,self.session),self.session)

    def test_oversize_chunk_is_rejected(self):
        token=a.firmar(self.manifest(10),self.session)
        class Request:
            async def stream(self): yield b'x'*11
        with self.assertRaises(HTTPException): asyncio.run(a.fragmento(0,token,Request(),self.session))

    def test_storage_usage_counts_all_pages(self):
        client=MagicMock(); client.get_paginator.return_value.paginate.return_value=[{'Contents':[{'Size':100}]},{'Contents':[{'Size':200},{'Size':300}]}]
        with patch.object(a,'modo',return_value='s3'),patch.object(a,'cliente_s3',return_value=client),patch.dict('os.environ',{'S3_BUCKET':'test'}):
            result=a.uso(None)
        self.assertEqual(result['bytes'],600)
        self.assertEqual(result['archivos'],3)
