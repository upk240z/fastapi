import os
import uuid
from pyzbar.pyzbar import decode, ZBarSymbol
from PIL import Image


def strip_image(img: Image):
    tmp_file = 'tmp/' + str(uuid.uuid1()) + '.' + ('png' if img.format == 'PNG' else 'jpg')
    img.save(tmp_file)
    strip_img = Image.open(tmp_file)
    os.remove(tmp_file)
    return strip_img


def scan(img: Image):
    results = decode(strip_image(img), symbols=[ZBarSymbol.QRCODE])

    codes = []
    for result in sorted(results, key=lambda x: x.rect.left):
        codes.append(result.data.decode('utf-8'))

    return codes
