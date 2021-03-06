import os
import datetime
import re
import hashlib
import logging
from io import BytesIO
from typing import List
from pyzbar.pyzbar import decode, ZBarSymbol
from PIL import Image
from config import Config

logging.basicConfig(
    filename=Config.basedir() + '/logs/' + datetime.datetime.today().strftime('%Y%m%d') + '.txt',
    level=logging.INFO,
)


def scan_qrcode(data: bytes) -> List[str]:
    img = Image.open(BytesIO(data))
    img_file = Config.basedir() + '/tmp/' + hashlib.sha256(data).hexdigest() + '.' + (
        'png' if img.format == 'PNG' else 'jpg'
    )
    logging.info('===== [receive]' + img_file + ' =====')
    if not os.path.exists(img_file):
        img.save(img_file)
    results = decode(Image.open(img_file), symbols=[ZBarSymbol.QRCODE])

    codes = []
    for result in sorted(results, key=lambda x: x.rect.left):
        detected_code = result.data.decode('utf-8')
        logging.info('[detected]' + detected_code)
        codes.append(detected_code)

    return codes


def parse_inspection(lines: List[str]) -> dict:
    table = str.maketrans('０１２３４５６７８９　', '0123456789 ')
    year_prefix = datetime.datetime.today().strftime('%Y')[0:2]

    pattern1 = re.compile(r'^2/-\s+/(\d{5})(\d{4})/(\d+)/(\d+)/')
    pattern2 = re.compile(r'2/(.{4})(.{3})(.)(.{4})/')

    matched1 = False
    matched2 = False

    info = {}

    for line in lines:
        line = line.translate(table)
        if not matched1:
            result = pattern1.match(line)
            if result:
                matched1 = True
                ymd = result.group(3)
                ym = result.group(4)
                info.update({
                    'kata': result.group(1),
                    'rui': result.group(2),
                    'inspection-fin-date': year_prefix + ymd[0:2] + '-' + ymd[2:4] + '-' + ymd[4:],
                    'first-month': year_prefix + ym[0:2] + '-' + ym[2:]
                })
                continue
        if not matched2:
            result = pattern2.match(line)
            if result:
                matched2 = True
                info['plate'] = {
                    'area': result.group(1).replace(' ', ''),
                    'class': result.group(2),
                    'hira': result.group(3),
                    'number': result.group(4).replace(' ', '0'),
                }

    result_code = 'error'
    if matched1 and matched2:
        result_code = 'success'
    elif matched1 or matched2:
        result_code = 'warning'

    return {
        'result': result_code,
        'info': info
    }
