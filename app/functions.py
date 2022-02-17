import os
import re
import uuid
from typing import List
from pyzbar.pyzbar import decode, ZBarSymbol
from PIL import Image
from config import Config


def scan_qrcode(img: Image):
    img_file = Config.basedir() + '/tmp/' + str(uuid.uuid1()) + '.' + ('png' if img.format == 'PNG' else 'jpg')
    img.save(img_file)
    results = decode(Image.open(img_file), symbols=[ZBarSymbol.QRCODE])

    codes = []
    for result in sorted(results, key=lambda x: x.rect.left):
        codes.append(result.data.decode('utf-8'))

    return codes


def parse_inspection(lines: List[str]):
    table = str.maketrans('０１２３４５６７８９　', '0123456789 ')

    pattern1 = re.compile(r'^2/-\s+/(\d{5})(\d{4})/(\d+)/(\d+)/')
    pattern2 = re.compile(r'2/(.{4})(.{3})(.)(.{4})/')

    matched1 = False
    matched2 = False

    parsed = {}

    for line in lines:
        line = line.translate(table)
        if not matched1:
            result = pattern1.match(line)
            if result:
                matched1 = True
                ymd = result.group(3)
                ym = result.group(4)
                parsed.update({
                    'kana': result.group(1),
                    'rui': result.group(2),
                    'inspection-fin-date': '20' + ymd[0:2] + '-' + ymd[2:4] + '-' + ymd[4:],
                    'first-month': '20' + ym[0:2] + '-' + ym[2:]
                })
                continue
        if not matched2:
            result = pattern2.match(line)
            if result:
                matched2 = True
                parsed['plate'] = {
                    'area': result.group(1).replace(' ', ''),
                    'class': result.group(2),
                    'hira': result.group(3),
                    'number': result.group(4).replace(' ', '0'),
                }

    return parsed
