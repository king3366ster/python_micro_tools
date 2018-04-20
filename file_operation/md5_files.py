# -*- coding:utf-8 -*-
import os, md5, base64

def md5_files(filename):
    with open(filename, 'rb') as fh:
        code = md5.new()
        code.update(fh.read())
        return code.hexdigest()

if __name__ == '__main__':
    print md5_files('zip_files.py')
