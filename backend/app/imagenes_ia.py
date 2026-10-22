"""Imágenes efímeras: validar contenido real y tamaño antes de enviarlo a Gemini."""
import base64
import binascii
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, ConfigDict, Field, model_validator

MAX_TOTAL = 2_400_000
MAX_IMAGES = 10


class ImageInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre: str = Field(min_length=1, max_length=150)
    mime_type: str = Field(pattern=r'^image/(jpeg|png|webp)$')
    data: str = Field(min_length=4, max_length=1_400_000)

    @model_validator(mode='after')
    def valid_image(self):
        try:
            raw=base64.b64decode(self.data, validate=True)
            if len(raw)>1_000_000:
                raise ValueError('Cada imagen debe ocupar como máximo 1 MB.')
            with Image.open(BytesIO(raw)) as picture:
                if picture.format != {'image/jpeg':'JPEG','image/png':'PNG','image/webp':'WEBP'}[self.mime_type]:
                    raise ValueError('El formato real no coincide con el tipo de imagen.')
                if picture.width*picture.height>16_000_000 or picture.width<16 or picture.height<16:
                    raise ValueError('Dimensiones de imagen no permitidas.')
                if getattr(picture,'n_frames',1)!=1:
                    raise ValueError('Adjunta imágenes estáticas.')
                picture.verify()
        except (binascii.Error, UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
            raise ValueError('La imagen está dañada o no tiene un formato permitido.') from exc
        return self

    def part(self):
        return {'inlineData':{'mimeType':self.mime_type,'data':self.data}}
