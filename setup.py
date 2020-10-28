#!/usr/bin/env python

from setuptools import setup
import os

DESCRIPTION = open(
    os.path.join(os.path.dirname(__file__), 'README.md')).read().strip()

setup(
    name='httmock',
    version='1.4.0',
    description='A mocking library for requests.',
    author='Patryk Zawadzki',
    author_email='patrys@room-303.com',
    url='https://github.com/patrys/httmock',
    py_modules=['httmock'],
    keywords=['requests', 'testing', 'mock'],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Testing',
        'Operating System :: OS Independent'],
    install_requires=['requests >= 1.0.0'],
    license='Apache-2.0',
    long_description=DESCRIPTION,
    long_description_content_type='text/markdown',
    test_suite='tests')
