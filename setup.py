#!/usr/bin/python3
# -*- encoding: utf-8 -*-

from setuptools import setup

__author__ = "H.C. Chen"

loc = {} # locals
with open("peforth/version.txt") as fp:
    exec(fp.read(),{},loc ) # later on we use: loc['__version__']

setup(
    name="peforth",
    version=loc['__version__'],
    packages=["peforth", ],
    license='The MIT License (MIT) Copyright © 2017 H.C. Chen',
    description="A FORTH programming language lives in python. Started with only two words 'code' and 'end-code'.",
    long_description=open("peforth/README.md", "r").read(),
    author="H.C. Chen",
    author_email="hcchen_1471@hotmail.com",
    url="https://github.com/hcchengithub/peforth",
    install_requires=[],
    data_files=[('lib/site-packages/peforth', ['peforth/peforth.f','peforth/quit.f'])],
)
