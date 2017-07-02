#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='arbalet_frontage',
    version='0.0.0',
    license="GNU General Public License 3",
    description="Arbalet Frontage, interactive building facade of Bordeaux University",
    url='http://github.com/arbalet-project',
    author="Yoan Mollard",
    author_email="contact@arbalet-project.org",
    long_description=open('README.md').read(),

    install_requires= ["zmq", "numpy", "flask", "flask_cors"],
    include_package_data=True,
    zip_safe=False,  # contains data files

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Games/Entertainment",
    ],

    packages=find_packages(),
    namespace_packages = ['arbalet', 'arbalet.frontage']
)
