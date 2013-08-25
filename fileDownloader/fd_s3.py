# -*- coding: utf-8 -*-

import base64
import hmac
import urllib
import httplib
import time

from hashlib import sha1 as sha
from urlparse import urlparse
from email.utils import formatdate

import S3

"""Notes:
            The S3 library from Amazon works well, except for the get, which reads the entire file into memory all at once.
            
            In a hacky way I have modified AWSAuthConnection by subclassing it to S3HttpLib. S3HttpLib._make_request will return
            an HTTPLib object, a path, and headers, with these you can request the key that you instantiated S3HttpLib with. See below for example.
            
            
            s3obj = S3HttpLib(AWSAccessKeyId, AWSSecretAccessKey) #Instantiate class
            conn, path, headers = s3obj._make_request('GET', 'ep-features', 'small_file', {}) #create httplib object, path, and headers
            conn.request("GET", path, headers=headers) #make Get request
            r1 = conn.getresponse() #get response from GET request
            print r1.status #get status code
            print r1.read() #read response body, ie, get the file.
"""

class S3HttpLib(S3.AWSAuthConnection):
    def _make_request(self, method, bucket='', key='', query_args={}, headers={}, data='', metadata={}):

        server = ''
        if bucket == '':
            server = self.server
        elif self.calling_format == S3.CallingFormat.SUBDOMAIN:
            server = "%s.%s" % (bucket, self.server)
        elif self.calling_format == S3.CallingFormat.VANITY:
            server = bucket
        else:
            server = self.server

        path = ''

        if (bucket != '') and (self.calling_format == S3.CallingFormat.PATH):
            path += "/%s" % bucket

        # add the slash after the bucket regardless
        # the key will be appended if it is non-empty
        path += "/%s" % urllib.quote_plus(key)


        # build the path_argument string
        # add the ? in all cases since 
        # signature and credentials follow path args
        if len(query_args):
            path += "?" + query_args_hash_to_string(query_args)

        is_secure = self.is_secure
        host = "%s:%d" % (server, self.port)
        while True:
            if (is_secure):
                connection = httplib.HTTPSConnection(host)
            else:
                connection = httplib.HTTPConnection(host)

            final_headers = S3.merge_meta(headers, metadata);
            # add auth header
            self._add_aws_auth_header(final_headers, method, bucket, key, query_args)
            
            return connection, path, final_headers

#            connection.request(method, path, data, final_headers)
#            resp = connection.getresponse()
#            if resp.status < 300 or resp.status >= 400:
#                return resp
#            # handle redirect
#            location = resp.getheader('location')
#            if not location:
#                return resp
#            # (close connection)
#            resp.read()
#            scheme, host, path, params, query, fragment \
#                    = urlparse.urlparse(location)
#            if scheme == "http":    is_secure = True
#            elif scheme == "https": is_secure = False
#            else: raise invalidURL("Not http/https: " + location)
#            if query: path += "?" + query
            # retry with redirect


DEFAULT_HOST = 's3.amazonaws.com'
PORTS_BY_SECURITY = { True: 443, False: 80 }
METADATA_PREFIX = 'x-amz-meta-'
AMAZON_HEADER_PREFIX = 'x-amz-'



    
AWSAccessKeyId = "AKIAI5EQIIMTQPZTM4DQ"
AWSSecretAccessKey = "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"

key = 'La_Boheme_Roh_2013_Part_2_1-78_MPEG-2-Fe.mpg'
#url = "ep-features.s3.amazonaws.com/"+urllib.quote(key)


#print __get__('ep-features.s3.amazonaws.com', '/'+urllib.quote(key), headers)
#print __get__('ep-features.s3.amazonaws.com', '/?notification', headers)

#conn = S3.AWSAuthConnection(AWSAccessKeyId, AWSSecretAccessKey)
#s3obj = S3HttpLib(AWSAccessKeyId, AWSSecretAccessKey)
#conn, path, headers = s3obj._make_request('GET', 'ep-features', key, {})
#buk = conn.list_bucket('ep-features')
#print buk.body
#print dir(getter), type(getter)
#conn.request("GET", path, headers=headers)
#r1 = conn.getresponse()
#print r1.status
#print r1.getheader('etag')  #gets you the md5hash
#open(key, 'wb').write(r1.read())