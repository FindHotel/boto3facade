#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages
import boto3facade.metadata as metadata

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


setup(
    name='boto3facade',
    packages=find_packages(),
    version=metadata.version,
    description=metadata.description,
    long_description=long_description,
    author=metadata.authors[0],
    author_mail=metadata.emails[0],
    url=metadata.url,
    license=metadata.license,
    # To integrate py.test with setuptools
    setup_requires=['pytest-runner'],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'click>=5.1',
        'boto3',
        'inflection>=0.3.1',
        'requests>=2.8.1'
    ],
    # Allow tests to be run with `python setup.py test'.
    tests_require=[
        'pytest>=2.5.1',
        'mock>=1.0.1',
        'flake8>=2.1.0'
    ],
)
