#! /usr/bin/env python
#-*- coding:utf-8 -*-

import urllib.request
import urllib.parse
import http.cookiejar
import json
from bs4 import BeautifulSoup

class HttpRequest:
    def __init__(self):
        cookie = http.cookiejar.CookieJar()
        #实例化一个全局opener
        cookie_handler = urllib.request.HTTPCookieProcessor(cookie)
        self.opener=  urllib.request.build_opener(cookie_handler)

    def getData(self, url, data = None):
        if data is None:
            url = url
        else:
            params = urllib.parse.urlencode(data)
            url = url + '?' + params
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        # req = urllib.request.Request(url, headers = headers, method='GET');
        # res_data = urllib.request.urlopen(url)
        res_data = self.opener.open(url, timeout = 20)
        return res_data

    # dataType form/text/json
    def postData(self, url, data = {}, header = {}, dataType = 'form', encoding = 'utf-8'):
        initHeader = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        if dataType == 'form':
            if isinstance(data, dict):
                data = urllib.parse.urlencode(data)
            tempHeader = {
                'Content-Type': 'application/x-www-form-urlencoded;'
            }
        elif dataType == 'json':
            if isinstance(data, dict):
                data = json.dumps(data)
            tempHeader = {
                'Content-Type': 'application/json;'
            }
        elif dataType == 'plain':
            tempHeader = {
                'Content-Type': 'text/plain;'
            }
        data = data.encode(encoding, 'ignore')
        tempHeader['Content-Length'] = len(data)
        headers = dict(initHeader)
        headers.update(tempHeader)
        headers.update(header)

        req = urllib.request.Request(url, data, headers = headers, method='POST');
        res_data = self.opener.open(req)
        return res_data

    def bs4HttpData(self, data):
        bsHandle = BeautifulSoup(data, 'lxml')
        return bsHandle

if __name__ == '__main__':

    q = {
        'wd': '测试'
    }
    t = HttpRequest()
    print (t.getData('http://www.baidu.com/s?wd=%E6%B5%8B%E8%AF%95').read().decode('utf8', 'ignore'))

    data = {
            'identity': '',
            'password': ''
        };
    res = t.postData('https://www.itjuzi.com/user/login', data = data, dataType = 'form')
    print (res.info())
