# -*- coding:utf-8 -*-
import urllib2, urllib, cookielib, json

# http请求的通用方法

class HttpRequest:
    def __init__(self, proxy=None):
        cj = cookielib.CookieJar()
        if proxy is not None:
            proxy_support = urllib2.ProxyHandler(proxy)
            self.opener = urllib2.build_opener(
                proxy_support, urllib2.HTTPCookieProcessor(cj))
        else:
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    def get_data(self, url, data=None):
        if data is None:
            url = url
        else:
            params = urllib.urlencode(data)
            url = url + '?' + params

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            # 'Accept-Encoding': 'gzip, deflate, sdch',
            # 'Accept-Language': 'zh-CN,zh;q=0.8',
            # 'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
##        print url
        req = urllib2.Request(url, headers=headers)
        res_data = self.opener.open(req, timeout=20)  # urllib2.urlopen(req)
        return res_data

    # dataType formdata/text/json/xml
    def post_data(self, url, data={}, header={}, dataType='formdata'):
        initHeader = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        if dataType == 'formdata':
            if isinstance(data, dict):
                data = urllib.urlencode(data)
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
            data = str(data)
            tempHeader = {
                'Content-Type': 'text/plain;'
            }
        tempHeader['Content-Length'] = len(data)
        headers = dict(initHeader.items() +
                       tempHeader.items() + header.items())

        req = urllib2.Request(url, data, headers=headers)
        res_data = self.opener.open(req)
        return res_data

if __name__ == '__main__':
    t = HttpRequest()
    print t.get_data('https://www.baidu.com').read()