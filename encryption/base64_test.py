# -*- coding:utf-8 -*-
import base64

def base64_encode(raw_str):
    return base64.b64encode(raw_str)

def base64_decode(raw_str):
    return base64.b64decode(raw_str)

if __name__ == '__main__':
    b64_e = base64_encode('111')
    print b64_e, base64_decode(b64_e)
