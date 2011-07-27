from setuptools import setup, find_packages
setup(name='fileDownloader.py', 
		version='0.4.0',
		description="Downloads files via HTTP or FTP",
		download_url="http://code.google.com/p/filedownload/downloads/list",
        packages = find_packages(exclude="test"),
		long_description="""Intro

This module is used for downloading files from the internet via http or ftp.

It supports basic http authentication and ftp accounts, and supports resuming downloads. It does not support https or sftp at this time. The main advantage of this package is it's ease of use, and pure pythoness. It only uses the Python standard library, so no dependencies to deal with, and no C to compile.

Usage

If a non-standard port is needed just include it in the url (http://example.com:7632).

    Simple

              downloader = fileDownloader.DownloadFile('http://example.com/file.zip')
              downloader.download()

    Use full path to download

             downloader = fileDownloader.DownloadFile('http://example.com/file.zip', "C:\\Users\\username\\Downloads\\newfilename.zip")
             downloader.download()

    Password protected download

             downloader = fileDownloader.DownloadFile('http://example.com/file.zip', "C:\\Users\\username\\Downloads\\newfilename.zip", ('username','password'))
             downloader.download()

    Resume

             downloader = fileDownloader.DownloadFile('http://example.com/file.zip')
             downloader.resume()""",
		classifiers=[
		"Programming Language :: Python",
		("Topic :: Software Development :: Libraries :: Python Modules"),
		],
		keywords='download',
		author='Joshua Banton',
		author_email='bantonj@gmail.com',
		url='http://bantonj.wordpress.com/software/open-source/',
		license='MIT')
