#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import cgitb, cgi, re
import docutils, os
import rstslide_template

import rstslide

cgitb.enable()

def get_input():
    import struct
    from codecs import decode
    def from_raw(match):
        s = match.group(1)
        buf = struct.pack('i', int(s))
        return decode(buf, 'utf-16')
    form = cgi.FieldStorage()
    result = unicode(form['rst'].value)
    return re.sub('&#([0-9]+);', from_raw, result)

logfile = open('/tmp/slide.log', 'at')


parser = docutils.parsers.rst.Parser()
document = docutils.utils.new_document('rstslide', rstslide.Settings())
parser.parse(get_input(), document)

pdffile = os.tmpnam()
document.walkabout(rstslide.Visitor(rstslide_template, document, pdffile))

print 'Content-Type: application/pdf'
print 'Content-Disposition: attachment; filename="slides.pdf"'
print 

print open(pdffile, 'rb').read(),
os.unlink(pdffile)
