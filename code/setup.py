#!/usr/bin/env python
from distutils.core import setup

setup(name='wiki2beamer',
    version='0.7alpha2',
    py_modules=['wiki2beamer'],
    scripts=['wiki2beamer.py'],
    description='Create LaTeX-beamer presentations with a wiki syntax',
    author='Kai Dietrich, Michael Rentzsch',
    author_email='mail@cleeus.de',
    url='http://wiki2beamer.sourceforge.net/'
)
