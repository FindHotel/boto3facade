#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup


setup(
    name='boto3facade',
    version='0.1',
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
        'flake8>=2.1.0',
    ],
)
