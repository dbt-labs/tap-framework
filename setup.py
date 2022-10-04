#!/usr/bin/env python

from setuptools import setup, find_packages
import os.path

setup(name='tap-framework',
      version='0.1.2',
      description='Framework for building Singer.io taps',
      author='Fishtown Analytics',
      url='http://fishtownanalytics.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_framework'],
      install_requires=[
          'singer-python>=5.1.0,<5.5.0',
          'backoff==1.3.2',
          'requests==2.20.0',
          'requests-oauthlib==0.8.0',
          'funcy==1.10.1',
      ],
      packages=['tap_framework'])
