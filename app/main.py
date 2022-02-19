import base64
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
from functions import scan_qrcode, parse_inspection
from config import Config


class QRCodeBase64Parameter(BaseModel):
    base64: str
    type: str = 'image/jpeg'


class QRCodeImageParameter(BaseModel):
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


def qr(data, is_base64=False):
    output = {
        'result': 'success',
        'message': None,
        'info': None,
    }

    try:
        if is_base64:
            data = base64.b64decode(data)
        img = Image.open(BytesIO(data))
        lines = scan_qrcode(img)
        output.update(parse_inspection(lines))
        if output['result'] == 'error':
            output['message'] = 'Detection failed'
        elif output['result'] == 'warning':
            output['message'] = 'Some detection failed'
        else:
            output['message'] = 'Success'
    except Exception as ex:
        output['result'] = 'error'
        output['message'] = str(ex)

    return output


@app.post('/qr-base64')
async def qrcode(parameter: QRCodeBase64Parameter):
    return qr(parameter.base64, True)


@app.post('/qr-img')
async def qrcode(data: bytes = Body(...)):
    return qr(data)
