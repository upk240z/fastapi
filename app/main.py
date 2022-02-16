import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
from functions import scan_qrcode, parse_inspection
from config import Config


class QRCodeParameter(BaseModel):
    base64: str
    type: str = 'image/jpeg'


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.get('origins'),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/qrcode')
async def qrcode(parameter: QRCodeParameter):
    output = {
        'result': True,
        'error': None,
    }

    try:
        encoded = parameter.base64
        decoded = base64.b64decode(encoded)
        img = Image.open(BytesIO(decoded))
        lines = scan_qrcode(img)
        output['parsed'] = parse_inspection(lines)
    except Exception as ex:
        output['result'] = False
        output['error'] = str(ex)

    return output
