# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from fmanalyser import __version__

setup(
    name = 'fmanalyser',
    version = __version__,
    author = "Gabriel Fournier",      
    author_email = "gabriel@gaftech.fr",
    description = "tools for pira.cz P175 FM Analyser",
    license = 'MIT',
    install_requires = (
        'pyserial >= 2.3', # Debian squeeze version. TODO: tests with Debian !
    ),
    packages = find_packages(),
    classifiers = (
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English'
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Scientific/Engineering :: Information Analysis'
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
    ),
)
