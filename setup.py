#!/usr/bin/env python

from setuptools import setup, find_packages
import os.path

setup(name='tap-framework',
      version='0.1.0',
      description='Framework for building Singer.io taps',
      author='Fishtown Analytics',
      url='http://fishtownanalytics.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_framework'],
      install_requires=[
          'singer-python>=5.1.0,<5.2.0',
          'backoff==1.3.2',
          'requests==2.18.4',
          'requests-oauthlib==0.8.0',
          'funcy==1.10.1',
      ],
      packages=['tap_framework'])
