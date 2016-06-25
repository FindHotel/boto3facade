"""Setuptools entry point."""

import codecs
import os
from setuptools import setup, find_packages

import boto3facade

dirname = os.path.dirname(__file__)

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError, RuntimeError):
    if os.path.isfile("README.md"):
        long_description = codecs.open(os.path.join(dirname, "README.md"),
                                       encoding="utf-8").read()
    else:
        long_description = "A simple facade for boto3"


setup(
    name="boto3facade",
    packages=find_packages(),
    version=boto3facade.__version__,
    package_data={'': ['*.ini']},
    description="A simple facade for Boto3",
    long_description=long_description,
    author="German Gomez Herrero, FindHotel BV",
    author_email="data@findhotel.net",
    url="http://github.com/findhotel/boto3facade",
    license="MIT",
    # To integrate py.test with setuptools
    setup_requires=["pytest-runner"],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "click>=5.1",
        "boto3",
        "inflection>=0.3.1",
        "requests>=2.8.1",
        "configparser>=3.5.0b2"
    ],
    # Allow tests to be run with `python setup.py test'.
    tests_require=[
        "pytest>=2.5.1",
        "mock>=1.0.1",
        "flake8>=2.1.0"
    ],
    zip_safe=False
)
