# -*- coding: utf-8 -*-
# pip install qcloud_cos_v4
# 腾讯云文件上传
# zwwbucket-1254265243.file.myqcloud.com
# zwwbucket - 1254265243.cossh.myqcloud.com(适用于JSON API)
# zwwbucket - 1254265243.cos.ap - shanghai.myqcloud.com(适用于XML API)
import os
import qcloud_cos
import click
import time
import json
import pdb

# 全局变量，腾讯及七牛
cos_client = None
cos_bucket_name = u'zwwbucket'
cos_image = 'http://zwwbucket-1254265243.file.myqcloud.com/'


def init_tencent():
    appid = 1254265243
    secret_id = u''
    secret_key = u''
    region_info = 'sh'
    cos_client = qcloud_cos.CosClient(
        appid, secret_id, secret_key, region=region_info)
    return cos_client


def put_tencent_image(client, key, data=None):
    # print u'http://zwwbucket-1254265243.file.myqcloud.com/%s' % (key,)

    request = qcloud_cos.UploadFileFromBufferRequest(
        bucket_name=cos_bucket_name,
        cos_path=key,
        data=data,
        insert_only=0
    )
    ret = client.upload_single_file_from_buffer(request)
    return ret


def del_tencent_image(client, key):
    request = qcloud_cos.DelFileRequest(
        bucket_name=cos_bucket_name,
        cos_path=key
    )
    ret = client.del_file(request)
    return ret


def list_tencent_image(client, key):
    request = qcloud_cos.ListFolderRequest(
        bucket_name=cos_bucket_name,
        cos_path=key,
        num=100,
    )
    ret = client.list_folder(request)
    return ret


def main(key_path=u'/'):
    tencent_client = init_tencent()
    items = list_tencent_image(tencent_client, key_path)
    for item in items[u'data'][u'infos']:
        key_name = u'%s%s' % (key_path, item[u'name'])
        ret = del_tencent_image(tencent_client, key_name)
        if ret[u'message'] != u'SUCCESS':
            print '   ', key_name, ret


if __name__ == '__main__':
    prev_time = time.time()
    for key_path in [u'/']:
        for i in range(0, 10000000):
            curr_time = time.time()
            print key_path, i, '##########', curr_time - prev_time
            main(key_path)
            prev_time = curr_time
