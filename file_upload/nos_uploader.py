# -*- coding:utf-8 -*-
# 网易云文件上传
import urllib2, urllib
import hmac
import random, time, datetime, re
import hashlib, base64

import nos

## test url
# access_key_id = ''
# access_key_secret = ''
# bucket = ''

## online url
access_key_id = ''
access_key_secret = ''
bucket = ''

end_point = ''

class FileTransfer:
    def __init__(self, basepath='test/', private=False):
        self.basepath = basepath
        self.private = private
        self.nos_client = nos.Client(
            access_key_id = access_key_id,
            access_key_secret = access_key_secret,
            transport_class = nos.transport.Transport,
            end_point = end_point,
            num_pools = 16,
            timeout = 20,
            max_retries = 3
        )

    def put_object(self, filename, filehandle):
        try:
            filename = '%s%s' % (self.basepath, filename)
            resp = self.nos_client.put_object(
                bucket = bucket,
                key = filename,
                body = filehandle.read()
            )
            return resp

        except nos.exceptions.ServiceException as e:
            return (
                'ServiceException: %s\n'
                'status_code: %s\n'
                'error_type: %s\n'
                'error_code: %s\n'
                'request_id: %s\n'
                'message: %s\n'
            ) % (
                e,
                e.status_code,
                e.error_type,
                e.error_code,
                e.request_id,
                e.message
            )

        except nos.exceptions.ClientException as e:
            return (
                'ClientException: %s\n'
                'message: %s\n'
            ) % (
                e,
                e.message
            )

    def put_large_object(self, filename, filehandle):
        try:
            filename = '%s%s' % (self.basepath, filename)
            size_m = 10 * 1024.0 * 1024.0
            filesize = filehandle.size / size_m
            # print filesize
            resp = self.nos_client.create_multipart_upload(
                    bucket = bucket,
                    key = filename
                )
            uploadId = resp['response'].find('UploadId').text
            # print uploadId

            sliceNum = 0
            for chunk in filehandle.chunks(int(size_m * 40)):
                # print sliceNum
                sliceNum += 1
                resp = self.nos_client.upload_part(
                    bucket = bucket,
                    key = filename,
                    part_num = sliceNum,
                    upload_id = uploadId,
                    body = chunk
                )

            rParts = self.nos_client.list_parts(
                bucket = bucket,
                key = filename,
                upload_id = uploadId
            )
            Parts = rParts['response']

            partETags=[]
            for part in Parts.findall('Part'):
                partETags.append({
                    'part_num': part.find('PartNumber').text,
                    'etag': part.find('ETag').text
                })
            resp = self.nos_client.complete_multipart_upload(
                bucket = bucket,
                key = filename,
                upload_id = uploadId,
                info = partETags
            )
            return resp

        except nos.exceptions.ServiceException as e:
            return (
                'ServiceException: %s\n'
                'status_code: %s\n'
                'error_type: %s\n'
                'error_code: %s\n'
                'request_id: %s\n'
                'message: %s\n'
            ) % (
                e,
                e.status_code,
                e.error_type,
                e.error_code,
                e.request_id,
                e.message
            )

        except nos.exceptions.ClientException as e:
            return (
                'ClientException: %s\n'
                'message: %s\n'
            ) % (
                e,
                e.message
            )

    def get_object(self, filename):
        try:
            filename = '%s%s' % (self.basepath, filename)
            resp = self.nos_client.get_object(
                bucket = bucket,
                key = filename
            )
            return resp

        except nos.exceptions.ServiceException as e:
            return (
                'ServiceException: %s\n'
                'status_code: %s\n'
                'error_type: %s\n'
                'error_code: %s\n'
                'request_id: %s\n'
                'message: %s\n'
            ) % (
                e,
                e.status_code,
                e.error_type,
                e.error_code,
                e.request_id,
                e.message
            )

        except nos.exceptions.ClientException as e:
            return (
                'ClientException: %s\n'
                'message: %s\n'
            ) % (
                e,
                e.message
            )

    def del_object(self, filename):
        try:
            filename = '%s%s' % (self.basepath, filename)
            resp = self.nos_client.delete_object(
                bucket = bucket,
                key = filename
            )
            return resp
        except nos.exceptions.ServiceException as e:
            return (
                'ServiceException: %s\n'
                'status_code: %s\n'
                'error_type: %s\n'
                'error_code: %s\n'
                'request_id: %s\n'
                'message: %s\n'
            ) % (
                e,
                e.status_code,
                e.error_type,
                e.error_code,
                e.request_id,
                e.message
            )

        except nos.exceptions.ClientException as e:
            return (
                'ClientException: %s\n'
                'message: %s\n'
            ) % (
                e,
                e.message
            )
    # http://api.nos.netease.com/accessControl.html#url
    def generateSignature(self, filename):

        NOSAccessKeyId = access_key_id

        Expires = int(time.time()) + 86400 * 10
        # Expires = 1927555200
        ContentMD5 = '';
        ContentType = '';
        ExpiresStr = Expires
        # ExpiresStr = datetime.datetime.utcfromtimestamp(Expires).strftime(
        #     "%a, %d %b %Y %H:%M:%S GMT"
        # )
        # ExpiresStr = datetime.datetime.fromtimestamp(Expires).strftime(
        #     "%a, %d %b %Y %H:%M:%S Asia/Shanghai"
        # )
        CanonicalizedHeaders = ''
        CanonicalizedResource = '/%s/%s' % (
            bucket, urllib2.quote(filename, '*')
        )
        print CanonicalizedResource
        origin_code = 'GET\n%s\n%s\n%s\n%s%s' % (
            ContentMD5,
            ContentType,
            ExpiresStr,
            CanonicalizedHeaders,
            CanonicalizedResource
        )

        hmac_sha1 = hmac.new(str(access_key_secret), origin_code, hashlib.sha256)
        b64_hmac_sha1 = base64.encodestring(hmac_sha1.digest())

        authorization_string = b64_hmac_sha1.rstrip('\n')

##        hashed = hmac.new(access_key_secret, origin_code, hashlib.sha256)
##        authorization_string = hashed.digest().encode("base64").strip().rstrip('\n')

        Signature  =  authorization_string #
        Signature = urllib2.quote(authorization_string, '*') # urllib.urlencode(origin_code)

        return '?NOSAccessKeyId=%s&Expires=%d&Signature=%s' % (NOSAccessKeyId, Expires, Signature)

    def generateUrl(self, filename):
        filename = '%s%s' % (self.basepath, unicode(filename))
        filename = filename.encode('utf-8', 'ignore')
        signature = ''
        if self.private:
            signature = self.generateSignature(filename)
        return 'http://%s.nos.netease.com/%s%s' % (
            bucket, urllib2.quote(filename, '*'), signature
        )
        # return 'http://%s.nos.netease.com/%s' % (bucket, urllib2.quote(filename, '*'))

if __name__ == '__main__':
    transferObj = FileTransfer(basepath = 'website/home/', private=False)
    filename = 'nos_uploader.py'
    with open(filename, 'r') as filetmp:
        nos_resp = transferObj.put_object(filename, filetmp)
        # nos_resp = transferObj.put_large_object(filename, filetmp)
        print nos_resp
        filelink = transferObj.generateUrl(filename)
        print filelink
