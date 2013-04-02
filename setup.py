#!/usr/bin/env python

from setuptools import setup, find_packages
import os

setup(name='httmock',
      version='1.0',
      description='A mocking library for requests.',
      author='Patryk Zawadzki',
      author_email='patrys@room-303.com',
      url='https://github.com/patrys/httmock',
      py_modules=['httmock'],
      keywords=['requests', 'testing', 'mock'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Testing',
          'Operating System :: OS Independent',
      ],
      install_requires=['requests'],
      long_description=open(
          os.path.join(os.path.dirname(__file__), 'README.md'),
      ).read().strip(),
)
