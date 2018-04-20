# -*- coding:utf-8 -*-
import re, urllib, urllib2, urlparse

# 查询链接是否404
file_name = 'find_404.csv'
url = raw_input('enter url:')
file_name = 'find_404_%s.csv' % url.replace('/', '').replace('.', '_').replace(':', '_')


def http_get_data(url):
    request = urllib2.Request(url)
    try:
        response = urllib2.urlopen(request, timeout=10)
        return response
    except urllib2.HTTPError as err:
        # print origin_url, url, err
        # print err
        return 404
    except Exception as err:
        # print origin_url, url, err
        return 404

def encode_url(url, base_url=None):
    if re.search('^tel:', url):
        return url
    if not re.search('^http[s]?:\/\/', url) and base_url:
        url = urlparse.urljoin(base_url, url)
    urlparser = urlparse.urlparse(url)
    url_path = urlparser.path
    url_query = urlparser.query
    if not re.search('%', url_path):
        url_path_new = urllib.quote(url_path, safe='')
        url = url.replace(url_path, url_path_new)
    url = url.replace('%2F', '/').replace('%26', '&').replace('%3D', '=').replace('%3B', ';').replace('&amp;', '&')
    url = re.sub('#.*$', '', url)
    return url

# 检查文本中的所有url地址
def find_url_links (content, base_url=''):
    if type(content) != unicode and type(content) != str:
        content = content.read()
    if type(content) == unicode:
        content = content.encode('utf-8', 'ignore')
    link_sets = set()
    for line in content.split('\n'):
        try:
            line = line.strip()
            links = re.findall(u'href\s*=\s*\"([^\"]+)\"', line)
            if links:
                links = map(lambda x: encode_url(x, base_url=base_url), links)
            srcs = re.findall(u'src\s*=\s*\"([^\"]+)\"', line)
            if srcs:
                srcs = map(lambda x: encode_url(x, base_url=base_url), srcs)
            link_sets = link_sets | set(links) | set(srcs)
            # srcs = re.findall()
        except Exception as what:
            print what
    return link_sets

# recurse 递归深度，1表示仅检查此页面链接，2表示此页面的链接的页面也检查，依次类推
def find_url_404 (url, recurse = 2, cur_recurse = 0, fake_links = set(), used_link_sets = set(), base_url=''):
    # url = encode_url(url)
    # 本页面查看是否404
    if url in used_link_sets:
        return (fake_links, used_link_sets)
    print '%d/%d: %s | %s' % (cur_recurse, recurse, url, base_url)
    http_read = http_get_data(url)
    used_link_sets.add(url)
    write_data(file_name, fake_links)
    # 额外添加需求
    if re.search('^(tel|javascript):', url):
        return (fake_links, used_link_sets)
    if http_read == 404:
        fake_links.add('%s,%s' % (url, base_url))
        return (fake_links, used_link_sets)
    if re.search('\.(jpg|png|gif|flv|m3u8|mp4|js|css)(\?[^\?]+)?$', url):
        return (fake_links, used_link_sets)
    if cur_recurse >= recurse:
        return (fake_links, used_link_sets)
    # 获取子页面链接
    cur_recurse += 1
    cnt = http_read.read()
    link_sets = find_url_links(cnt, base_url=url)
    for link in link_sets:
        # print cur_recurse, link
        try:
            (fake_links, used_link_sets) = find_url_404(link, base_url=url, recurse=recurse, cur_recurse=cur_recurse, fake_links=fake_links, used_link_sets=used_link_sets)
        except Exception as what:
            pass
    return (fake_links, used_link_sets)

def write_data(file_name, fake_links):
    with open(file_name, 'w') as f:
        for line in fake_links:
            f.write(line.decode('utf-8', 'ignore').encode('gbk', 'ignore'))
            f.write('\n')

if __name__ == '__main__':
    # url = 'https://www.baidu.com/'
    # file_name = 'find_404_%s.csv' % url.replace('/', '').replace('.', '_').replace(':', '_')
    (fake_links, used_link_sets) = find_url_404(url, recurse=8)
    write_data(file_name, fake_links)
