import unittest
import os
import downloader


def calculate_md5(filename, block_size=2**20):
    """Returns MD% checksum for given file.
    """
    import hashlib

    md5 = hashlib.md5()
    try:
        with open(filename, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                md5.update(data)
    except IOError:
        print('File \'' + filename + '\' not found!')
        return None
    except:
        return None
    return md5.hexdigest()


class TestHttpDownload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = []

    def test_download(self):
        down = downloader.Download("http://ovh.net/files/1Mb.dat")
        self.files.append("1Mb.dat")
        down.download()
        assert os.path.exists("1Mb.dat")
        assert calculate_md5("1Mb.dat") == "62501d556539559fb422943553cd235a"

    def test_partial_download(self):
        down = downloader.Download("http://ovh.net/files/1Mb.dat")
        self.files.append("1Mb.dat")
        down.partial_download(0, 50000)
        assert os.path.exists("1Mb.dat")
        assert calculate_md5("1Mb.dat") == "b331251c69ed7ededd8fd2c8a729e073"

    def test_resume(self):
        down = downloader.Download("http://ovh.net/files/1Mb.dat")
        self.files.append("1Mb.dat")
        down.partial_download(0, 50000)
        down.resume()
        assert os.path.exists("1Mb.dat")
        assert calculate_md5("1Mb.dat") == "62501d556539559fb422943553cd235a"

    def test_rate_limit_exception(self):
        down = downloader.Download("http://ovh.net/files/1Mb.dat")
        self.files.append("1Mb.dat")
        with self.assertRaises(downloader.TokenBucketError) as context:
            down.enable_rate_limit(5000, 10000)
        print(context.exception)
        self.assertTrue('rate_burst must be > 8192' in str(context.exception))

    def test_rate_limit(self):
        down = downloader.Download("http://ovh.net/files/1Mb.dat")
        self.files.append("1Mb.dat")
        down.enable_rate_limit(500000)
        down.download()
        assert os.path.exists("1Mb.dat")
        assert calculate_md5("1Mb.dat") == "62501d556539559fb422943553cd235a"

    def test_check_exists(self):
        down = downloader.Download("http://ovh.net/files/1Mb.dat")
        exists = down.check_exists()
        self.assertTrue(exists)
        down = downloader.Download("http://ovh.net/files/not_exists.dat")
        exists = down.check_exists()
        self.assertFalse(exists)

    def test_ftp_download(self):
        down = downloader.Download("ftp://speedtest.tele2.net/512KB.zip")
        self.files.append("512KB.zip")
        down.download()
        assert os.path.exists("512KB.zip")
        assert calculate_md5("512KB.zip") == "59071590099d21dd439896592338bf95"

    def test_ftp_download_password(self):
        down = downloader.Download("ftp://test.rebex.net/readme.txt", auth=("demo", "password"))
        self.files.append("readme.txt")
        down.download()
        assert os.path.exists("readme.txt")
        assert calculate_md5("readme.txt") == "d1f2b721bf97a3b6ae0c7975f5a0a11b"

    def test_ftp_download_wrong_password(self):
        down = downloader.Download("ftp://test.rebex.net/readme.txt", auth=("demo", "wrong"))
        self.files.append("readme.txt")
        with self.assertRaises(downloader.urllib.error.URLError) as context:
            down.download()
        self.assertTrue('User cannot log in.' in str(context.exception))

    def tearDown(self):
        for file in self.files:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
