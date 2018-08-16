#encoding:utf-8
import urllib
import os

def download_schedule(a, b, c):
    '''''
    a:已经下载的数据块
    b:数据块的大小
    c:远程文件的大小
   '''
    per = 100.0 * a * b / c
    if per > 100 :
        per = 100
    print '%.2f%%' % per

def download_file (fileurl, filepath):
    filename = fileurl.split('/')[-1]
    local = os.path.join(filepath, filename)
    print filename, filepath
    urllib.urlretrieve(fileurl, local, download_schedule)
    print 'done'

if __name__ == '__main__':
    fileurl = 'http://www.python.org/ftp/python/2.7.5/Python-2.7.5.tar.bz2'
    filepath = os.getcwd()
    download_file(fileurl, filepath)