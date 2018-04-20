# -*- coding: utf-8 -*-
import os, shutil, stat, pdb, re, json
import urllib, urllib2, time
import pymysql, redis
import click, hashlib
import pandas as pd
from sqlalchemy import create_engine
# from elasticsearch import Elasticsearch

# 开发文档同步到搜索引擎

db_dev = {
    'search_url': 'http://223.252.215.121',
    'host': '10.240.76.63',
    'user': 'admin',
    'password': '',
    'database': 'test',
    'port': 3306,
    'redis_host': '127.0.0.1',
    'redis_port': 6379,
    'redis_auth': '',
}

db_test = {
    'search_url': 'http://223.252.215.121',
    'host': '10.172.122.20',
    'user': 'neimdemo',
    'password': '^46DA0(va',
    'database': 'nim_webdoc',
    'port': 3306,
    'redis_host': '127.0.0.1',
    'redis_port': 63792,
    'redis_auth': '',
}

db_online = {
    'search_url': 'http://10.122.157.59',
    'host': '10.172.73.217',
    'user': 'nim_manage',
    'password': 'Ml7ku-<wX',
    'database': 'web_doc',
    'port': 3306,
    'redis_host': '10.164.165.133',
    'redis_port': 6379,
    'redis_auth': '4oqkksxHvW3K',
}

tb_name = u'webdoc_content'
tb_bbs_name = u'pre_forum_post'

def generate_md5(src):
    dest = hashlib.md5()
    dest.update(src)
    return dest.hexdigest()

def send_sh_cmd(cmd):
    output = os.popen(cmd)
    return output.read()

def load_git(branch='master'):
    git_url = 'ssh://git@github.com/yunxin-doc/yunxin-web-doc.git'
    dest_git_path = 'git/yunxin-doc'
    if not os.path.exists(dest_git_path):
        cmd = 'git clone -b %s %s %s' % (branch, git_url, dest_git_path)
        res = send_sh_cmd(cmd)
        # print u'%s: git clone %s' % (name, res)
        os.chmod(dest_git_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        return res
    else:
        os.chdir('./%s' % dest_git_path)
        send_sh_cmd('git checkout *')
        send_sh_cmd('git checkout %s' % branch)
        res = send_sh_cmd('git pull')
        # print u'%s: git pull %s' % (name, res)
        os.chdir('../../')
        return res

def http_post_data(url, data={}):
    headers = {
        'Content-Type': 'application/json;charset=utf-8'
    }
    post_data = json.dumps(data)
    request = urllib2.Request(url, data=post_data, headers=headers)
    response = urllib2.urlopen(request)
    return response

def http_delete_data(url):
    request = urllib2.Request(url=url)
    request.get_method = lambda: 'DELETE'
    response = urllib2.urlopen(request)
    return response

def get_file_tree(src):
    file_list = []

    def wander_dir(src_path):
        if not os.path.exists(src_path):
            return
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
                    wander_dir(src_file)
    wander_dir(src)
    return file_list

def parse_title(line):
    link_hash = ''
    link_content = ''
    line = re.sub(r'^#+\s+', '', line)
    if re.search(r'\<[^\<\s]+\s+id=[\'\"]([^\"\']+)[\"\']\s*\>', line):
        link_hash = re.findall(
            r'\<[^\<\s]+\s+id=[\'\"]([^\"\']+)[\"\']\s*\>', line)[0]
        link_hash = u'#%s' % link_hash
        link_content = repl_html_tag(line)
    else:
        link_content = line.strip()
    return {
        'link_content': link_content,
        'link_hash': link_hash,
    }

def repl_html_tag(line):
    line = re.sub(r'<[\/]{0,1}[a-z]+[^>]*>', ' ', line)
    line = re.sub(r'<!--[^-]+-->', ' ', line)
    line = re.sub(r'<!DOCTYPE[^>]+>', ' ', line)
    return line.strip()

def get_link_client(link_name):
    link_client = ''
    if link_name.lower().find('ios') > 0:
        link_client = 'ios'
    elif link_name.lower().find('android') > 0:
        link_client = 'android'
    elif link_name.lower().find('windows') > 0:
        link_client = 'windows'
    elif link_name.lower().find('mac') > 0:
        link_client = 'mac'
    elif link_name.lower().find('linux') > 0:
        link_client = 'linux'
    elif link_name.lower().find('web') > 0:
        link_client = 'web'
    elif link_name.lower().find('unity') > 0:
        link_client = 'unity'
    elif link_name.lower().find('cocos') > 0:
        link_client = 'cocos'
    elif link_name.lower().find(u'服务端') > 0:
        link_client = 'server'
    elif link_name.lower().find(u'pc') > 0:
        link_client = 'windows'
    return link_client

def get_markdown_docs(src_file):
    file_list = get_file_tree(src_file)
    link_map = {}
    for file_name in file_list:
        link_name = file_name.replace(
            src_file, u'/docs/product').replace(u'\\', '/').replace(u'.md', '')
        file_title = re.findall(r'\/([^\/]+)$', link_name)[0]
        if file_name.find(u'.md') <= 0:
            continue
        with open(file_name, 'r') as f_h:
            link_name_temp = link_name
            link_title = ''
            lines = f_h.read()
            lines = re.split(r'[\r\n]', lines)
            for line in lines:
                line = line.strip().decode('utf-8', 'ignore')
                if line == '':
                    continue
                elif re.search(r'^```', line) or re.search(r'^---$', line):
                    continue
                elif re.search(r'^#{1,4}\s', line):
                    title_obj = parse_title(line)
                    link_name_temp = u'%s%s' % (
                        link_name, title_obj['link_hash'])
                    link_content = title_obj['link_content']
                    link_title = link_content
                else:
                    link_content = repl_html_tag(line)
                if link_content != '' and link_title != '':
                    if link_name_temp not in link_map:
                        link_map[link_name_temp] = {
                            'file_title': file_title,
                            'link_content': link_content,
                            'link_title': link_title,
                        }
                    else:
                        link_map[link_name_temp]['link_content'] += ' %s' % link_content
    docs_for_save = []
    for link_name in link_map:
        link_content = link_map[link_name]['link_content']
        link_content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r' \1 ', link_content)
        link_content = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', link_content)
        link_content = link_content.strip()
        link_title = link_map[link_name]['link_title']
        link_prod = link_name.replace(u'/docs/product/', '')
        link_prod = link_prod[:link_prod.find('/')]
        link_client = get_link_client(link_name)

        if link_content != '':
            docs_for_save.append({
                'title': link_map[link_name]['file_title'],
                'link_name': link_name,
                'link_title': link_title,
                'link_content': link_content,
                'link_client': link_client,
                'link_prod': link_prod,
            })
    return docs_for_save

def get_api_docs(src_file):
    file_list = get_file_tree(src_file)
    docs_for_save = []
    for file_name in file_list:
        if file_name.find('.html') >= 0:
            link_name = file_name.replace(
                '\\', '/').replace('git/yunxin-doc/doc/', '/docs/interface/')
            title = link_name.split('/')[3]
            with open (file_name, 'r') as f_h:
                link_content = f_h.read()
                link_content = repl_html_tag(link_content)
                link_content = re.sub(r'\s+', ' ', link_content)
                link_content = link_content.decode('utf-8', 'ignore')

                link_title = re.split(r'\s+', link_content)[0]
                link_client = get_link_client(title)
                docs_for_save.append({
                    'title': title,
                    'link_name': link_name,
                    'link_title': link_title,
                    'link_content': link_content,
                    'link_client': link_client,
                    'link_prod': u'API文档',
                })
    return docs_for_save

def read_redis (redis_inst, url):
    hkey = 'yx::webdoc::stat'
    score = redis_inst.hget(hkey, url)
    redis_inst.hdel(hkey, url)
    if not score:
        score = 0
    return score

def init_mysql(db):
    conn = pymysql.connect(
        host=db['host'], port=db['port'], user=db['user'], passwd=db['password'], db=db['database'], use_unicode=True, charset="utf8")
    cur = conn.cursor()
    cur.execute(u'UPDATE %s SET `status` = 0' % tb_name)
    conn.commit()
    #关闭指针对象
    cur.close()
    #关闭连接对象
    conn.close()

# 查询原有记录，没有插入，status2，比较content的MD5，如果与先前不一致，存入status2,否则status1，如果没有该篇文档status0
def save_to_mysql(docs, db, doc_type='md', init_score=8):
    conn = pymysql.connect(
        host=db['host'], port=db['port'], user=db['user'], passwd=db['password'], db=db['database'], use_unicode=True, charset="utf8")
    cur = conn.cursor()
    for doc in docs:
        url = doc['link_name']
        title = doc['title'].replace('"', ' ').replace('\'', ' ')
        sub_title = doc['link_title'].replace('"', ' ').replace('\'', ' ')
        content = doc['link_content'].replace('"', ' ').replace('\'', ' ')
        client = doc['link_client']
        prod = doc['link_prod']
        extra = generate_md5(content.encode('utf-8'))
        score = int(read_redis(db['redis_inst'], url)) + init_score
        ret = cur.execute(
            u'SELECT * FROM `%s` WHERE `url` = "%s"' % (tb_name, url))
        if ret:
            doc_info = cur.fetchone()
            origin_extra = doc_info[-2]
            if origin_extra != extra or score != 0:
            # print u'update %s' % url
                cur.execute(
                    u'UPDATE `%s` SET title="%s", sub_title="%s", client="%s", prod="%s", content="%s", type="%s", status=2, extra="%s", score=score+"%d" WHERE url="%s"' % (tb_name, title, sub_title, client, prod, content, doc_type, extra, score, url))
            else:
                cur.execute(u'UPDATE `%s` SET status=1 WHERE url="%s"' % (tb_name, url))
            conn.commit()
        else:
            # print 'insert %s' % url
            cur.execute(
                u'INSERT INTO `%s` (url, title, sub_title, client, prod, content, type, status, extra, score) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", 2, "%s", "%d");' % (tb_name, url, title, sub_title, client, prod, content, doc_type, extra, score))
            conn.commit()
    #关闭指针对象
    cur.close()
    #关闭连接对象
    conn.close()
    print 'sync mysql saved!'

def query_from_mysql(db, query = 'select * from %s' % tb_name):
    engine = create_engine('mysql://%s:%s@%s:3306/%s?charset=utf8' %
                           (db['user'], db['password'], db['host'], db['database']))
    df = pd.read_sql(query, engine)
    return df

# def index_elastic_search (data, db):
#     search_url = '%s/elasticsearch/' % db['search_url']
#     es = Elasticsearch(search_url)
#     index_data = {
#         'title': data['title'],
#         'subtitle': data['sub_title'],
#         'url': data['url'],
#         'content': data['content'],
#         'client': data['client'],
#         'type': data['type'],
#         'prod': data['prod'],
#         'score': data['score'],
#     }
#     res = es.index(index='website', doc_type='docs', id=data['id'], body=index_data)
#     print res

def index_docs_search (data, db):
    url = '%s/elasticsearch/website/%s/%d?pretty' % (
        db['search_url'], 'docs', data['id'])
    index_data = {
        'title': data['title'],
        'subtitle': data['sub_title'],
        'url': data['url'],
        'content': data['content'],
        'content_en': data['content'],
        'client': data['client'],
        'type': data['type'],
        'prod': data['prod'],
        'score': data['score'],
    }
    res = http_post_data(url, data = index_data)
    return res.read().decode('utf-8')

def delete_docs_search (data, db):
    url = '%s/elasticsearch/website/%s/%d?pretty' % (
        db['search_url'], 'docs', data['id'])
    res = http_delete_data(url)
    return res.read().decode('utf-8')

def query_docs_search (data, db):
    url = '%s/elasticsearch/website/%s/_search?pretty' % (
        db['search_url'], 'docs')
    res = http_post_data(url, data)
    return res.read().decode('utf-8')

def sync_doc_tosql (db):
    # 同步文档，存储到数据库
    print load_git(branch=db['branch'])
    init_mysql(db)
    print 'init mysql done'

    src_file = u'git/yunxin-doc/md'
    docs = get_markdown_docs(src_file)
    save_to_mysql(docs, db)

    src_file = u'git/yunxin-doc/doc'
    docs = get_api_docs(src_file)
    save_to_mysql(docs, db, init_score=1)

def sync_doc_fromsql (db, force = False):
    df = query_from_mysql(db)
    for (index, rows) in df.iterrows():
        search_data = rows.to_dict()
        try:
            if search_data['status'] == 1 and not force:
                print 'ignore data id: %d' % search_data['id']
            elif search_data['status'] > 0:
                index_docs_search(search_data, db)
                print 'put data id: %d' % search_data['id']
            else:
                delete_docs_search(search_data, db)
                print 'del data id: %d' % search_data['id']
        except Exception as what:
            print search_data['id'], what
        time.sleep(0.002)

@click.command()
@click.option('--env', default='dev', help='pyenv:dev/test/online')
@click.option('--force', default='false', help='force:true/false')
def main(env, force):
    if env == 'dev':
        db = db_dev
        db['branch'] = 'developer'
    elif env == 'test':
        db = db_test
        db['branch'] = 'developer'
    elif env == 'online':
        db = db_online
        db['branch'] = 'master'

    pool = redis.ConnectionPool(host=db['redis_host'], port=db['redis_port'], password=db['redis_auth'])
    redis_inst = redis.Redis(connection_pool=pool)
    db['redis_inst'] = redis_inst

    sync_doc_tosql(db)
    if force == 'true':
        sync_doc_fromsql(db, force=True)
    else:
        sync_doc_fromsql(db)

    # 查询语句
    query = {
        'query': {
            'match': {
                'content': u'需要调用'
            }
        }
    }
    query_docs_search(query, db)

if __name__ == '__main__':
    main()
