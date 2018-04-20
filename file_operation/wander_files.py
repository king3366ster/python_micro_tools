# -*- coding:utf-8 -*-
import os, re

def wander_dir(src_path, file_list = []):
    if type(src_path) == str:
        src_path = src_path.decode('utf-8', 'ignore')
    if not os.path.exists(src_path):
        raise Exception('path not exists: %s' % src_path)
    elif os.path.isfile(src_path):
        file_list.append(src_path)
    elif os.path.isdir(src_path):
        files = os.listdir(src_path)
        for file_name in files:
            if re.search(r'\.git$', file_name):
                continue
            src_file = os.path.join(src_path, file_name)
            # print u'cp file %s' % dst_file
            if os.path.isfile(src_file):
                file_list.append(src_file)
            elif os.path.isdir(src_file):
                file_list = wander_dir(src_file, file_list=file_list)
    return file_list

if __name__ == '__main__':
    print wander_dir('web_docs_dev')
