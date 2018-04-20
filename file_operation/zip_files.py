# -*- coding:utf-8 -*-
import os, re, zipfile

def wander_dir(src_path, file_list=[]):
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


def zip_files(src_path):
    if type(src_path) == str:
        src_path = src_path.decode('utf-8', 'ignore')
    if not os.path.exists(src_path):
        raise Exception('path not exists: %s' % src_path)
    if re.search(u'\.zip$', src_path):
        return
    if os.path.isfile(src_path) and re.search(u'\.[^\.]+$'):
        dst_path = re.sub(u'\.[^\.]+$', u'.zip', src_path)
    else:
        dst_path = u'%s.zip' % src_path
    with zipfile.ZipFile(dst_path, 'w') as f:
        file_list = wander_dir(src_path)
        for file_name in file_list:
            print file_name
            f.write(file_name)

def unzip_files(src_path):
    if type(src_path) == unicode:
        src_path = src_path.decode('utf-8', 'ignore')
    if not os.path.exists(src_path):
        raise Exception('path not exists: %s' % src_path)
    with zipfile.ZipFile(src_path) as f:
        dst_path = re.sub('\.zip$', '', src_path)
        if os.path.isdir(dst_path):
            pass
        else:
            os.mkdir(dst_path)
        for names in f.namelist():
            if type(names) == unicode:
                names = names.decode('utf-8', 'ignore')
            f.extract(names, dst_path)

if __name__ == '__main__':
    # zip_files('web_docs_dev')
    unzip_files('nim-web-doc-web.zip')

