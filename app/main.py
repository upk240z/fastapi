import base64
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
from functions import scan
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

@app.get('/debug')
async def debug():
    return {
        'basedir': Config.basedir(),
        'settings': Config.get('settings'),
        'origins': Config.get('origins'),
    }


@app.post('/qrcode')
async def qrcode(parameter: QRCodeParameter):
    output = {
        'result': True,
        'decoded': {},
        'error': None,
    }

    try:
        encoded = parameter.base64
        decoded = base64.b64decode(encoded)
        img = Image.open(BytesIO(decoded))
        lines = scan(img)

        table = str.maketrans('０１２３４５６７８９　', '0123456789 ')

        pattern1 = re.compile(r'^2/-\s+/(\d{5})(\d{4})/(\d+)/(\d+)/')
        pattern2 = re.compile(r'2/(.{4})(.{3})(.)(.{4})/')

        matched1 = False
        matched2 = False

        for line in lines:
            line = line.translate(table)
            if not matched1:
                result = pattern1.match(line)
                if result:
                    matched1 = True
                    output['decoded']['kata'] = result.group(1)
                    output['decoded']['rui'] = result.group(2)
                    ymd = result.group(3)
                    output['decoded']['inspection_fin_date'] = '20' + ymd[0:2] + '-' + ymd[2:4] + '-' + ymd[4:]
                    ym = result.group(4)
                    output['decoded']['first_month'] = '20' + ym[0:2] + '-' + ym[2:]
                    continue
            if not matched2:
                result = pattern2.match(line)
                if result:
                    matched2 = True
                    output['decoded']['plate'] = {}
                    output['decoded']['plate']['riku'] = result.group(1).replace(' ', '')
                    output['decoded']['plate']['code'] = result.group(2)
                    output['decoded']['plate']['hira'] = result.group(3)
                    output['decoded']['plate']['no'] = result.group(4).replace(' ', '0')
    except Exception as ex:
        output['result'] = False
        output['error'] = str(ex)

    return output