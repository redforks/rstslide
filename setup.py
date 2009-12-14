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
        data_files = [('/usr/share/rstslide/', ['slide-test.rst',
            'slide-test-en.rst', 'bwp_template.py',
            'angel-star.png', 'snow-angel.gif', 'sleep.jpg', 'title.png',
            'README']),
            ('/usr/share/rstslide/web/', ['web/index.html']),
            ('/usr/share/rstslide/web/cgi-bin/', ['web/cgi-bin/convert.py'])]
    )
