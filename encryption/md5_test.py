# -*- coding:utf-8 -*-
import md5

def md5_text(text):
    code = md5.new()
    code.update(text)
    return code.hexdigest()

if __name__ == '__main__':
    plain_text = '1123'
    print md5_text(plain_text)
