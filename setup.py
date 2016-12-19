#!/usr/bin/env python

from setuptools import setup
import os

LICENSE = open(
    os.path.join(os.path.dirname(__file__), 'LICENSE')).read().strip()

DESCRIPTION = open(
    os.path.join(os.path.dirname(__file__), 'README.md')).read().strip()

setup(
    name='httmock',
    version='1.2.6',
    description='A mocking library for requests.',
    author='Patryk Zawadzki',
    author_email='patrys@room-303.com',
    url='https://github.com/patrys/httmock',
    py_modules=['httmock'],
    keywords=['requests', 'testing', 'mock'],
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Operating System :: OS Independent'],
    install_requires=['requests >= 1.0.0'],
    license=LICENSE,
    long_description=DESCRIPTION,
    test_suite='tests')
