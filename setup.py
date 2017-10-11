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
    description="A programmable python debugger allows you to abruptly setup procedures to investigate your program code when you're at a breakpoint.",
    long_description=open("README.rst", "r").read(),
    author="H.C. Chen",
    author_email="hcchen5600@gmail.com",
    url="https://github.com/hcchengithub/peforth",
    install_requires=[],
    data_files=[('lib/site-packages/peforth', ['peforth/peforth.f','peforth/quit.f','peforth/version.txt','peforth/peforth.selftest'])],
)
