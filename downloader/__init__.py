"""Downloads files from http or ftp locations.

Copyright Joshua Banton"""
import os
import urllib.request, urllib.error, urllib.parse
import ftplib
import urllib.parse
import urllib.request, urllib.parse, urllib.error
import socket
from time import time, sleep

name = "file-downloader"


class Download:
    """This class is used for downloading files from the internet via http or ftp.
    It supports basic http authentication and ftp accounts, and supports resuming downloads. 
    It does not support https or sftp at this time.
    
    The main advantage of this class is it's ease of use, and pure pythoness. It only uses the Python standard library, 
    so no dependencies to deal with, and no C to compile.
    
    #####
    If a non-standard port is needed just include it in the url (http://example.com:7632).
    
    #Rate Limiting:
        rate_limit = the average download rate in Bps
        rate_burst = the largest allowable burst in bytes
    
    Basic usage:
        Simple
            downloader = fileDownloader.DownloadFile('http://example.com/file.zip')
            downloader.download()
         Use full path to download
             downloader = fileDownloader.DownloadFile('http://example.com/file.zip', "C:/Users/username/Downloads/newfilename.zip")
             downloader.download()
         Basic Authentication protected download
             downloader = fileDownloader.DownloadFile('http://example.com/file.zip', "C:/Users/username/Downloads/newfilename.zip", ('username','password'))
             downloader.download()
         Resume
             downloader = fileDownloader.DownloadFile('http://example.com/file.zip')
            downloader.resume()
    """

    def __init__(self,
                 url=None,
                 download_path=None,
                 auth=None,
                 timeout=120.0,
                 retries=5,
                 fast_start=False):
        """Note that auth argument expects a tuple, ('username','password')."""
        self.url = url
        self.urlFileName = None
        self.progress = 0
        self.fileSize = None
        self.download_path = download_path
        self.type = self.get_type()
        self.auth = auth
        self.timeout = timeout
        self.retries = retries
        self.fast_start = fast_start
        self.cur_retry = 0
        self.cur = 0
        self.rate_limit_bucket = None
        if not self.fast_start:
            try:
                self.url_file_size = self.get_url_file_size()
            except urllib.error.HTTPError:
                self.url_file_size = None
        else:
            self.url_file_size = None
        if not self.download_path:  # if no filename given pulls filename from the url
            self.download_path = self.get_url_filename()

    def __download_file(self, url_obj, file_obj, call_back=None):
        """starts the download loop"""
        if not self.fast_start:
            self.fileSize = self.get_url_file_size()
        while 1:
            if self.rate_limit_bucket:
                if not self.rate_limit_bucket.spend(8192):
                    sleep(1)
                    continue
            try:
                data = url_obj.read(8192)
            except (socket.timeout, socket.error) as t:
                print("caught ", t)
                self.__retry()
                break
            if not data:
                file_obj.close()
                break
            file_obj.write(data)
            self.cur += 8192
            if call_back:
                call_back(cursize=self.cur)

    def __retry(self):
        """auto-resumes up to self.retries"""
        if self.retries > self.cur_retry:
            self.cur_retry += 1
            if self.get_local_file_size() != self.url_file_size:
                self.resume()
        else:
            print('retries all used up')
            return False, "Retries Exhausted"

    def __auth_http(self):
        """handles http basic authentication"""
        pass_man = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        # this creates a password manager
        pass_man.add_password(None, self.url, self.auth[0], self.auth[1])
        # because we have put None at the start it will always
        # use this username/password combination for  urls
        auth_handler = urllib.request.HTTPBasicAuthHandler(pass_man)
        # create the AuthHandler
        opener = urllib.request.build_opener(auth_handler)
        urllib.request.install_opener(opener)

    def __auth_ftp(self):
        """handles ftp authentication"""
        ftp_handler = urllib.request.FTPHandler()
        ftp_url = self.url.replace('ftp://', '')
        req = urllib.request.Request(
            "ftp://%s:%s@%s" % (self.auth[0], self.auth[1], ftp_url))
        req.timeout = self.timeout
        ftp_obj = ftp_handler.ftp_open(req)
        return ftp_obj

    def __start_http_partial(self, startPos, endPos, callBack=None):
        with open(self.download_path, "wb") as f:
            if self.auth:
                self.__auth_http()
            req = urllib.request.Request(self.url)
            req.headers['Range'] = 'bytes=%s-%s' % (startPos, endPos)
            urllib2_obj = urllib.request.urlopen(req, timeout=self.timeout)
            self.__download_file(urllib2_obj, f, call_back=callBack)

    def __start_http_resume(self, restart=None, call_back=None):
        """starts to resume HTTP"""
        cur_size = self.get_local_file_size()
        if cur_size >= self.url_file_size:
            return False
        self.cur = cur_size
        if restart:
            f = open(self.download_path, "wb")
        else:
            f = open(self.download_path, "ab")
        if self.auth:
            self.__auth_http()
        req = urllib.request.Request(self.url)
        req.headers['Range'] = 'bytes=%s-%s' % (cur_size,
                                                self.get_url_file_size())
        urllib2_obj = urllib.request.urlopen(req, timeout=self.timeout)
        self.__download_file(urllib2_obj, f, call_back=call_back)

    def __start_ftp_resume(self, restart=None):
        """starts to resume FTP"""
        cur_size = self.get_local_file_size()
        if cur_size >= self.url_file_size:
            return False
        if restart:
            f = open(self.download_path, "wb")
        else:
            f = open(self.download_path, "ab")
        ftper = ftplib.FTP(timeout=60)
        parse_obj = urllib.parse.urlparse(self.url)
        base_url = parse_obj.hostname
        url_port = parse_obj.port
        b_path = os.path.basename(parse_obj.path)
        g_path = parse_obj.path.replace(b_path, "")
        un_encg_path = urllib.parse.unquote(g_path)
        file_name = urllib.parse.unquote(os.path.basename(self.url))
        ftper.connect(base_url, url_port)
        ftper.login(self.auth[0], self.auth[1])
        if len(g_path) > 1:
            ftper.cwd(un_encg_path)
        ftper.sendcmd("TYPE I")
        ftper.sendcmd("REST " + str(cur_size))
        down_cmd = "RETR " + file_name
        ftper.retrbinary(down_cmd, f.write)

    def enable_rate_limit(self, rate_burst=9000, rate_limit=1000):
        if rate_burst < 8192:
            raise TokenBucketError("rate_burst must be > 8192")
        self.rate_limit_bucket = TokenBucket(rate_burst, rate_limit)

    def get_url_filename(self):
        """returns filename from url"""
        return urllib.parse.unquote(os.path.basename(self.url))

    def get_url_file_size(self):
        """gets file size of remote file from ftp or http server"""
        if self.type == 'http':
            if self.auth:
                self.__auth_http()
            urllib2_obj = urllib.request.urlopen(
                self.url, timeout=self.timeout)
            size = urllib2_obj.headers.get('content-length')
            return int(size)

    def get_local_file_size(self):
        """gets file size of local file"""
        size = os.stat(self.download_path).st_size
        return size

    def get_type(self):
        """returns protocol of url (ftp or http)"""
        url_type = urllib.parse.urlparse(self.url).scheme
        return url_type

    def check_exists(self):
        """Checks to see if the file in the url in self.url exists"""
        if self.auth:
            if self.type == 'http':
                self.__auth_http()
        elif self.type == 'ftp':
            return "not yet supported"
        try:
            urllib.request.urlopen(self.url, timeout=self.timeout)
        except urllib.error.HTTPError:
            return False
        return True
            

    def download(self, call_back=None):
        """starts the file download"""
        self.cur_retry = 0
        self.cur = 0
        with open(self.download_path, "wb") as f:
            if self.auth:
                if self.type == 'http':
                    self.__auth_http()
                    urllib2_obj = urllib.request.urlopen(
                        self.url, timeout=self.timeout)
                    self.__download_file(urllib2_obj, f, call_back=call_back)
                elif self.type == 'ftp':
                    self.url = self.url.replace('ftp://', '')
                    auth_obj = self.__auth_ftp()
                    self.__download_file(auth_obj, f, call_back=call_back)
            else:
                urllib2_obj = urllib.request.urlopen(
                    self.url, timeout=self.timeout)
                self.__download_file(urllib2_obj, f, call_back=call_back)
            return True

    def resume(self, call_back=None):
        """attempts to resume file download"""
        url_type = self.get_type()
        if url_type == 'http':
            self.__start_http_resume(call_back=call_back)
        elif url_type == 'ftp':
            self.__start_ftp_resume()

    def partial_download(self, start_pos, end_pos, call_back=None):
        """downloads a piece of a file, only supports HTTP"""
        if self.type == 'http':
            self.__start_http_partial(start_pos, end_pos, callBack=call_back)
        elif self.type == 'ftp':
            raise DownloadError("Partial download doesn't support ftp.")


class DownloadError(Exception):
    def __init__(self, message=''):
        self.message = message


class TokenBucket:
    """An implementation of the token rate_limit_bucket algorithm.
       Slightly modified from http://code.activestate.com/recipes/511490-implementation-of-the-token-rate_limit_bucket-algorithm/"""

    def __init__(self, bucket_size, fill_rate):
        """tokens is the total tokens in the rate_limit_bucket. fill_rate is the
        rate in tokens/second that the rate_limit_bucket will be refilled."""
        self.capacity = float(bucket_size)
        self._tokens = float(bucket_size)
        self.fill_rate = float(fill_rate)
        self.timestamp = time()

    def spend(self, tokens):
        """Spend tokens from the rate_limit_bucket. Returns True if there were
        sufficient tokens otherwise False."""
        if tokens <= self.get_tokens():
            self._tokens -= tokens
        else:
            return False
        return True

    def get_tokens(self):
        now = time()
        if self._tokens < self.capacity:
            delta = self.fill_rate * (now - self.timestamp)
            self._tokens = min(self.capacity, self._tokens + delta)
        self.timestamp = now
        return self._tokens


class TokenBucketError(Exception):
    def __init__(self, message=''):
        self.message = message
