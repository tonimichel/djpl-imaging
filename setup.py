#! /usr/bin/env python
import os
from setuptools import setup, find_packages

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name='djpl-imaging',
    version='0.1',
    description='a django-productline feature to add python-imaging support to your project',
    long_description=read('README.rst'),
    license='The MIT License',
    keywords='django, django-productline, imaging, thumbnails',
    author='Toni Michel',
    author_email='toni@schnapptack.de',
    url="https://github.com/tonimichel/djpl-imaging",
    packages=find_packages(),
    package_dir={'imaging': 'imaging'},
    include_package_data=True,
    scripts=[],
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent'
    ],
    install_requires=[]
)

