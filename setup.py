#!/usr/bin/env python

from setuptools import setup, find_packages
import os.path

setup(name='tap-framework',
      version='0.2.0',
      description='Framework for building Singer.io taps',
      author='dbt Labs',
      url='https://getdbt.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_framework'],
      install_requires=[
          'singer-python>=5.1.0,<5.14',
          'backoff>=1.3.2,<=1.8.0',
          'requests>=2.18.4,<2.29',
          'requests-oauthlib>=0.8.0,<1.4',
          'funcy>=1.10.1,<1.19',
      ],
      packages=['tap_framework'])
