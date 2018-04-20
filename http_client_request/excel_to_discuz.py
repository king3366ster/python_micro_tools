# -*- encoding:utf-8 -*-
# -*- coding:utf-8 -*-
import urllib2, urllib, cookielib, json, time, re
import pdb
import pandas as pd

# 读取excel数据，发帖到论坛

class HttpRequest:
    def __init__(self, host='', proxy=None):
        cj = cookielib.CookieJar()
        if proxy is not None:
            proxy_support = urllib2.ProxyHandler(proxy)
            self.opener = urllib2.build_opener(
                proxy_support, urllib2.HTTPCookieProcessor(cj))
        else:
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        self.host = host

    def post_data(self, url_path, data={}, header={}):
        url = '%s%s' % (self.host, url_path)
        # print url
        data = urllib.urlencode(data)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }
        req = urllib2.Request(url, data, headers=headers)
        res_data = self.opener.open(req)
        return res_data
    
    def login(self, username, password, formhash=''):
        url_path = 'member.php?mod=logging&action=login&loginsubmit=yes&handlekey=login'
        data = {
            'formhash': formhash,
            'referer': self.host,
            'loginfield': 'username',
            'username': username,
            'password': password,
            'questionid': 0,
            'answer': ''
        }
        res = self.post_data(
            url_path,
            data = data
        )
        # print res.read().decode('utf-8', 'ignore')
        return res.getcode()

    def login_admin(self, username, password, sid=''):
        url_path = 'admin.php'
        data = {
            'sid': sid,
            'frames': 'yes',
            'admin_username': username,
            'admin_password': password,
            'admin_questionid': 0,
            'admin_answer': '',
            'submit': '提交'
        }
        res = self.post_data(
            url_path,
            data = data
        )
        print res.read().decode('utf-8', 'ignore')
        return res.getcode()

    def get_thread_formhash(self, fid=1):
        # url_path = 'forum.php?mod=ajax&action=checkpostrule&ac=newthread&inajax=yes'
        url_path = 'forum.php?mod=post&action=newthread&fid=%d' % fid
        url = '%s%s' % (self.host, url_path)
        req = urllib2.Request(url)
        res_data = self.opener.open(req)
        thread_data = res_data.read().decode('utf-8', 'ignore')
        formhash = thread_data[thread_data.find('name="formhash"'):]
        formhash = formhash[formhash.find('value=')+6:]
        formhash = formhash[1:formhash.find('/>')-2]
        return formhash.strip()

    def get_admin_sid(self):
        # url_path = 'forum.php?mod=ajax&action=checkpostrule&ac=newthread&inajax=yes'
        url_path = 'admin.php'
        url = '%s%s' % (self.host, url_path)
        req = urllib2.Request(url)
        res_data = self.opener.open(req)
        thread_data = res_data.read().decode('utf-8', 'ignore')
        formhash = thread_data[thread_data.find('name="sid"'):]
        formhash = formhash[formhash.find('value=')+6:]
        formhash = formhash[1:formhash.find('>')-2]
        return formhash.strip()

    def send_thread(self, fid=1, subject='', message='', formhash=''):
        url_path = 'forum.php?mod=post&action=newthread&fid=%d&extra=&topicsubmit=yes' % fid
        data = {
            'formhash': formhash,
            'posttime': int(time.time()),
            'wysiwyg': 1,
            'subject': subject,
            'message': message,
            'allownoticeauthor': 1,
            'usesig': 1,
            'save': ''
        }
        res = self.post_data(
            url_path,
            data=  data
        )
        return res

    def format_thread(self, content, offset = 0):
        content = content.replace('<b>', '[b]').replace('</b>', '[/b]').replace('<code>', '[b]').replace('</code>', '[/b]').replace('<pre>', '[code]').replace('</pre>', '[/code]')
        content = re.sub(r'<a href=\"([^\"]+)\">', r'[url=\1]', content)
        content = content.replace('</a>', '[/url]')
        content = re.sub(r'<img src=\"([^\"]+)\"\s*>', r'[img]\1[/img]', content)
        content = re.sub(r'\s+', ' ', content)
        content = content.replace('\r', '').replace('\n', ' ')
        content = content.replace('<ul>', '').replace('<li>', ' ').replace('<br>', '\n')
        content = content.replace('</ul>', '\n').replace('</li>', '\n')
        content = content.replace('<tr>', '').replace('</tr>', '\n')
        content = content.replace('<td>', '').replace('</td>', ' ')
        content = content.replace('<table>', '\n').replace('</table>', ' ')
        replace_arr = re.findall(r'\[url=#KB\d+\]', content)
        if len(replace_arr) > 0:
            for item in replace_arr:
                tid = item[8:-1]
                tid = int(tid) + offset
                content = content.replace(item, '[url=forum.php?mod=viewthread&tid=%d]' % tid)
        return content

if __name__ == '__main__':
    host = 'http://127.0.0.1/discuz/'
    xhr = HttpRequest(host)
    username = ''
    password = ''
    fid = 1
    offset = 1

    sid = xhr.get_admin_sid()
    print 'sid:', sid
    login_code = xhr.login_admin(username, password, sid=sid)
    print 'login:', login_code

    formhash = xhr.get_thread_formhash(fid)
    print 'formhash:', formhash
    # login_code = xhr.login(username, password, formhash)
    # print 'login:', login_code

    df = pd.read_excel('support_content.xlsx')
    # df = df.iloc[7:]
    f = open('error.log', 'w')
    # pdb.set_trace()
    for index, item in df.iterrows():
        subject = u'[经验分享]' + item.title
        message = item.content
        fid = item.fid
        print index, subject, fid
        subject = subject.encode('utf-8', 'ignore')
        message = xhr.format_thread(message, offset).encode('utf-8', 'ignore')
        res = xhr.send_thread(fid=fid, subject=subject, message=message, formhash=formhash)
        time.sleep(0.5)
        # print res.getcode()
        result = res.read().decode('utf-8', 'ignore')
        error_msg = ''
        if result.find(u'class="alert_error"') >= 0:
            error_msg = result[result.find(u'class="alert_error"'):]
            error_msg = error_msg[24: error_msg.find('</p>')]
            error_msg = u'KB:%s, ERR:%s\n' % (item.kb, error_msg)
        elif result.find(u'class="alert_info"') >= 0:
            error_msg = result[result.find(u'class="alert_info"'):]
            error_msg = error_msg[23: error_msg.find('</p>')]
            error_msg = u'KB:%s, ERR:%s\n' % (item.kb, error_msg)
        if error_msg != '':
            print error_msg
            error_msg = error_msg.encode('utf-8', 'ignore')
            f.write(error_msg)
            res = xhr.send_thread(fid=fid, subject='supporter_kb_%s_%s' % (item.kb, error_msg), message=message, formhash=formhash)

    f.close()
