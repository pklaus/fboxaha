#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A Python package with a class to query the status of AVM
SmartHome devices via HTTP AHA connected to a Fritz!BOX.
"""

from setuptools import setup

setup(
    name = 'fboxaha',
    author = 'Philipp Klaus',
    author_email = 'philipp.l.klaus@web.de',
    url = "http://github.com/pklaus/fboxaha",
    version = '0.6',
    description = __doc__,
    long_description = __doc__,
    license = 'GPL',
    packages = ['fboxaha'],
    scripts = ['scripts/test_fboxaha'],
    install_requires = [
        'requests>=2.6.0',
    ],
    keywords = 'Fritz!BOX AHA smarthome',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
    ]
)

