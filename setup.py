#!/usr/bin/python3
# -*- encoding: utf-8 -*-

from setuptools import setup

__author__ = "H.C. Chen"

loc = {} # locals
with open("peforth/version.txt") as fp:
    exec(fp.read(),{},loc ) # later on we use: loc['__version__']

setup(
    zip_safe = False,
    name="peforth",
    version=loc['__version__'],
    packages=["peforth", ],
    license='The MIT License (MIT) Copyright © 2024 H.C. Chen',
    description="A FORTH programming language built on python.",
    long_description=open("README.rst", "r").read(),
    author="H.C. Chen",
    author_email="hcchen5600@gmail.com",
    url="https://github.com/hcchengithub/peforth",
    install_requires=[],
    package_data={
        '': ['version.txt', '*.f', '*.selftest', '*.json'],
    }
)
