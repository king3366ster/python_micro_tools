# -*- encoding:utf-8 -*-
import json, urllib, urllib2
import pandas as pd

# 技术支持网站数据导出到excel

def post_data(url, data={}, header={}):
    data = urllib.urlencode(data)
    headers = {
        # 'Content-Type': 'application/x-www-form-urlencoded;'
        'Content-Type': 'application/json;charset=utf-8'
    }

    req = urllib2.Request(url, data, headers=headers)
    res_data = urllib2.urlopen(req)
    return res_data

if __name__ == '__main__':
    url = 'http://hi163.cloud/kb/php/forum.php'
    res = post_data(url)
    cnt = res.read() #.decode('unicode-escape').encode('utf-8', 'ignore')
    cnt = json.loads(cnt)
    df = pd.DataFrame(cnt)
    df.to_excel('support_content.xlsx', encoding='utf-8', index=False)
    # for item in cnt:
    #     print item
    # with open('test.html', 'w') as f:
    #     f.write(cnt)
