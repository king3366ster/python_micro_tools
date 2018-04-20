# -*- coding:utf-8 -*-
# install https://github.com/tesseract-ocr/tesseract/wiki
# pip install pillow, pytesseract

from PIL import Image, ImageGrab, ImageEnhance
import numpy as np
import math, pdb
import pytesseract

def blacken_img(im):
    (w, h) = im.size
    wn = w * 2
    hn = h * 2
    im_t = im
    im_t = im_t.convert('L')
    im_t = im_t.resize((wn, hn))
    enh_ins = ImageEnhance.Contrast(im_t)
    contrast = 4
    im_t = enh_ins.enhance(contrast)
    for i in range(0, wn):
        for j in range(0, hn):
            pix = im_t.getpixel((i, j))
            if pix > 200:
                pix = 255
            else:
                pix = 0
            im_t.putpixel((i, j), pix)
    return im_t

def format_code (code):
    code = code.replace(' ', '')
    if len(code) > 6:
        code = code.replace('1]', '0').replace('l]', '0')
        code = code.replace('[11', '00')
    code = code.replace('D', '0').replace('O', '0').replace('U', '0')
    code = code.replace('?', '7').replace('T', '7').replace('J', '7')
    code = code.replace('B', '8')
    return code

def analyse_code (im_t):
    code = pytesseract.image_to_string(
        im_t, lang='eng', config="-psm 7 nobatch")
    # code = pytesseract.image_to_string(im_t)
    # code = format_code(code)
    return code

if __name__=='__main__':
    # im = ImageGrab.grab()
    im = Image.open('test.jpg')
    (width, height) = im.size
    im = im.crop((180, 430, 280, 480))
    im = blacken_img(im)
    print analyse_code(im)
    im.show()
