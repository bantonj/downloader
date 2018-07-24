from setuptools import setup, find_packages
setup(name='file-downloader', 
		version='0.5.1',
		description="Downloads files via HTTP or FTP",
        packages = find_packages(exclude="test"),
		long_description="""Intro

This module is used for downloading files from the internet via http or ftp.

It supports basic http authentication and ftp accounts, and supports resuming downloads. It does not support https or sftp at this time. The main advantage of this package is it's ease of use, and pure pythoness. It only uses the Python standard library, so no dependencies to deal with, and no C to compile.

Usage

If a non-standard port is needed just include it in the url (http://example.com:7632).

    Simple

              downloader = downloader.Download('http://example.com/file.zip')
              downloader.download()

    Use full path to download

             downloader = downloader.Download('http://example.com/file.zip', "/Users/username/Downloads/newfilename.zip")
             downloader.download()

    Password protected download

             downloader = downloader.Download('http://example.com/file.zip', "/Users/username/Downloads/newfilename.zip", ('username','password'))
             downloader.download()

    Resume

             downloader = downloader.Download('http://example.com/file.zip')
             downloader.resume()""",
		classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
		],
		keywords='download',
		author='Joshua Banton',
		author_email='bantonj@gmail.com',
		url='https://github.com/bantonj/downloader',
		license='MIT')
