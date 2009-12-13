#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import cgitb, cgi
import docutils, os
import rstslide_template

import rstslide

cgitb.enable()

logfile = open('/tmp/slide.log', 'at')

form = cgi.FieldStorage()

parser = docutils.parsers.rst.Parser()
document = docutils.utils.new_document('rstslide', rstslide.Settings())
input = form['rst'].value
parser.parse(input, document)

pdffile = os.tmpnam()
document.walkabout(rstslide.Visitor(rstslide_template, document, pdffile))

print 'Content-Type: application/pdf'
print 'Content-Disposition: attachment; filename="slides.pdf"'
print 

print open(pdffile, 'rb').read(),
os.unlink(pdffile)
