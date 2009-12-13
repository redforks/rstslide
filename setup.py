#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from distutils.core import setup

setup(
        name='rstslide', 
        version='0.1.0',
        author='Red Forks',
        author_email='redforks@gmail.com',
        py_modules=['rstslide', 'rstslide_template'],
        requires=['pycairo', 'docutils', 'pil'],
    )
