#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import docutils.parsers.rst
from docutils.nodes import SkipChildren, Node
import cairo, math
import Image
from os import tmpnam, unlink

import rstslide_template

#TODO: field support, like author, company...
#TODO: howto host to web

class ListOptions(object):
    def __init__(self, num, type, prefix, suffix):
        self.num = num
        self.type = type
        self.prefix = prefix
        self.suffix = suffix

    def get_and_inc_num(self):
        result = self.num
        self.num += 1
        return result

    def str_and_inc(self):
        def int2roman(number):
            numerals={1:"I", 4:"IV", 5:"V", 9: "IX", 10:"X", 40:"XL", 50:"L",
                      90:"XC", 100:"C", 400:"CD", 500:"D", 900:"CM", 1000:"M"}
            result=""
            for value, numeral in sorted(numerals.items(), reverse=True):
                while number >= value:
                    result += numeral
                    number -= value
            return result

        loweralpha = lambda x: chr(ord('a') + x - 1)
        upperalpha = lambda x: chr(ord('A') + x - 1)
        lowerroman = lambda x: int2roman(x).lower()
        upperroman = int2roman
        arabic = str

        result = self.prefix + locals()[self.type](self.num) + self.suffix
        self.num += 1
        return result

class Visitor(docutils.utils.nodes.NodeVisitor):
    def __init__(self, template, document, output_file):
        docutils.utils.nodes.NodeVisitor.__init__(self, document)
        surface = cairo.PDFSurface(output_file, 800, 600)
        self.fields = {}
        ctx = self.__ctx = cairo.Context(surface)
        self.__set_template(template)
        ctx.set_line_width(1.0)
        self.__list_level = 0
        self.__cur_list_option = [] # item should be ListOptions
        self.__indents = []

    def __set_template(self, template):
        self.__template = template
        self.switch_page_type('default')

    def switch_page_type(self, type_name):
        page_type = getattr(self.__template, type_name)()
        self.__page_type = page_type
        ctx = self.__ctx
        ctx.select_font_face(page_type.font_face, cairo.FONT_SLANT_NORMAL,
                cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(page_type.font_size)
        ctx.move_to(0, page_type.content_pos[1])
        self.__cur_para_margin_left = page_type.margin_left
        self.__cur_para_margin_right = page_type.margin_right

        ctx.save()
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.paint()
        ctx.set_source_rgb(0, 0, 0)
        page_type.render_background(ctx, self.fields)
        ctx.restore()
        
    def do_visit_text(self, text):
        text = text.replace('\n', '')
        while text:
            w = 0
            for idx, ch in enumerate(text):
                self.__ctx.show_text(ch)
                w = self.__ctx.get_current_point()[0]
                if w >= self.__cur_para_margin_right:
                    text = text[idx+1:]
                    break
            else:
                text = ''
            if text:
                self.__newline()
                self.__ctx.rel_move_to(self.__cur_para_margin_left,
                        self.__page_type.para_line_height)

    def visit_Text(self, text):
        self.do_visit_text(text.astext())

    def __newline(self):
        ctx = self.__ctx
        pos = ctx.get_current_point()
        extents = ctx.text_extents(u'啊')
        ctx.move_to(0, pos[1] + extents[3])

    def visit_strong(self, node):
        ctx = self.__ctx
        ctx.save()
        cur_face = ctx.get_font_face()
        ctx.select_font_face(cur_face.get_family(), cur_face.get_slant(),
                cairo.FONT_WEIGHT_BOLD)

    def depart_strong(self, node):
        self.__ctx.restore()

    def visit_emphasis(self, node):
        ctx = self.__ctx
        ctx.save()
        cur_face = ctx.get_font_face()
        ctx.select_font_face(cur_face.get_family(), cairo.FONT_SLANT_ITALIC,
                cur_face.get_weight())

    depart_emphasis = depart_strong

    def visit_literal(self, node):
        ctx = self.__ctx
        ctx.save()
        cur_face = ctx.get_font_face()
        ctx.select_font_face(self.__page_type.monospace_font_face, cur_face.get_slant(),
                cur_face.get_weight())

    depart_literal = depart_strong

    def visit_block_quote(self, quote):
        self.__cur_para_margin_left = self.__page_type.block_quote_margin_left
        self.__cur_para_margin_right = self.__page_type.block_quote_margin_right
        ctx = self.__ctx
        ctx.save()
        ctx.set_font_size(self.__page_type.block_quote_font_size)
        ctx.select_font_face(self.__page_type.block_quote_font_face,
                cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

    def depart_block_quote(self, quote):
        self.__cur_para_margin_left = self.__page_type.margin_left
        self.__cur_para_margin_right = self.__page_type.margin_right
        self.__ctx.restore()
        self.__ctx.rel_move_to(0, self.__page_type.para_after_height)

    def visit_paragraph(self, para):
        self.__ctx.rel_move_to(self.__cur_para_margin_left, 0)

    def depart_paragraph(self, para):
        self.__newline()
        self.__ctx.rel_move_to(0, self.__page_type.para_after_height)

    def visit_title(self, title):
        ctx = self.__ctx
        ctx.save()
        ctx.move_to(*self.__page_type.title_pos)
        ctx.set_font_size(self.__page_type.title_font_size)
        ctx.set_source_rgb(*self.__page_type.title_color)

    def indent(self, size):
        self.__indents.append(size)
        self.__cur_para_margin_left += size

    def undent(self):
        size = self.__indents.pop()
        self.__cur_para_margin_left -= size

    def visit_list_item(self, list_item):
        ctx = self.__ctx
        pos = ctx.get_current_point()
        extents = ctx.text_extents(u'啊')
        def draw_bullet():
            ctx.new_sub_path()
            if self.__list_level in (1, 2):
                ctx.arc(self.__cur_para_margin_left, pos[1], 3, 0, math.pi * 2)
                if self.__list_level == 1:
                    ctx.fill()
                else:
                    ctx.stroke()
            else:
                p = self.__cur_para_margin_left, pos[1]
                ctx.rectangle(p[0] - 3, p[1] - 3, 6, 6)
                ctx.fill()
            ctx.move_to(0, pos[1] + extents[3] // 2)
            self.indent(8)

        def draw_arabic():
            ctx.move_to(self.__cur_para_margin_left, pos[1] + extents[3] // 2)
            ctx.show_text(self.__cur_list_option[-1].str_and_inc())
            p = ctx.get_current_point()
            self.indent(p[0] - self.__cur_para_margin_left + 8)
            ctx.move_to(0, pos[1] + extents[3] // 2)

        draw_lowerroman = draw_upperroman = draw_upperalpha = \
                draw_loweralpha = draw_arabic

        locals()['draw_' + self.__cur_list_option[-1].type]()

    def depart_list_item(self, node):
        self.undent()

    def depart_title(self, title):
        self.__ctx.restore()
        self.__ctx.move_to(0, self.__page_type.content_pos[1])

    def unknown_visit(self, node):
        raise NotImplementedError(
            '%s visiting unknown node type: %s'
            % (self.__class__, node.__class__.__name__))

    def unknown_departure(self, node):
        raise NotImplementedError(
            '%s departing unknown node type: %s'
            % (self.__class__, node.__class__.__name__))

    def visit_new_page(self, node):
        self.__ctx.show_page()
        self.switch_page_type('default')
        self.__ctx.move_to(0, self.__page_type.content_pos[1])

    def visit_pause(self, node):
        self.__ctx.copy_page()

    def visit_system_message(self, msg):
        print msg.astext()
        raise SkipChildren()

    def visit_enumerated_list(self, node):
        start = node['start'] if node.has_key('start') else 1
        enumtype = node['enumtype'] if node.has_key('enumtype') else 'bullet'
        prefix = node['prefix'] if node.has_key('prefix') else ''
        suffix = node['suffix'] if node.has_key('suffix') else ''
        self.__cur_list_option.append(ListOptions(start, enumtype, prefix,
            suffix))
        if self.__list_level:
            self.__cur_para_margin_left += self.__page_type.sub_list_indent
        self.__list_level += 1

    visit_bullet_list = visit_enumerated_list

    def depart_enumerated_list(self, node):
        self.__cur_list_option.pop()
        self.__list_level -= 1
        if self.__list_level:
            self.__cur_para_margin_left -= self.__page_type.sub_list_indent
        self.__ctx.rel_move_to(0, self.__page_type.para_after_height)

    depart_bullet_list = depart_enumerated_list

    def get_node_attr(self, node, key, default):
        return node[key] if node.has_key(key) else default

    def visit_image(self, node):
        def scale_surface(surface, new_width, new_height):
            result = surface.create_similar(cairo.CONTENT_COLOR, int(new_width),
                    int(new_height))
            ct = cairo.Context(result)
            ct.scale(new_width / surface.get_width(), new_height /
                    surface.get_height())
            ct.set_source_surface(surface)
            # To avoid getting the edge pixels blended with 0 alpha, which would 
            # occur with the default EXTEND_NONE.
            ct.get_source().set_extend(cairo.EXTEND_REFLECT)
            ct.set_operator(cairo.OPERATOR_SOURCE)
            ct.paint()
            return result

        def load_image(file):
            if not file.endswith('.png'):
                img = Image.open(file)
                file = tmpnam()
                img.save(file, 'png')
                result = cairo.ImageSurface.create_from_png(file)
                unlink(file)
                return result
            return cairo.ImageSurface.create_from_png(file)

        ctx = self.__ctx
        ctx.save()
        img_surface = load_image(node['uri'])
        width = float(node['width']) if node.has_key('width') else \
            img_surface.get_width()
        height = float(node['height']) if node.has_key('height') else \
            img_surface.get_height()
        scale = float(node['scale']) if node.has_key('scale') else 100
        if scale != 100:
            width = width * scale / 100
            height = height * scale / 100

        align = node['align'] if node.has_key('align') else 'center'
        img_surface = scale_surface(img_surface, width, height)

        pos = ctx.get_current_point()
        x = pos[0]
        if align == 'center':
            width = self.__cur_para_margin_right - self.__cur_para_margin_left
            x = (width - img_surface.get_width()) / 2
            x += self.__cur_para_margin_left
        elif align == 'right':
            x = self.__cur_para_margin_right - \
                img_surface.get_width()
        pos = x, pos[1]
        
        ctx.set_source_surface(img_surface, x, pos[1])
        ctx.paint()

        ctx.restore()
        ctx.move_to(*pos)
        ctx.rel_move_to(0, img_surface.get_height())
        self.__newline()
        ctx.rel_move_to(0, self.__page_type.para_after_height)

    def visit_page_type(self, node):
        self.switch_page_type(node.type)

    def visit_template(self, node):
        template = __import__(node.template)
        self.__set_template(template)

    def visit_output_to(self, output_to):
        pos = self.__page_type.get_output_rect(output_to.output)
        self.__ctx.move_to(0, pos[1])
        self.__cur_para_margin_left = pos[0]
        self.__cur_para_margin_right = pos[0] + pos[2]

    def visit_field(self, field):
        self.fields[field[0].astext()] = field[1].astext()
        raise SkipChildren()

nonef = lambda self, node: None
def log_visit(cls, name):
    setattr(cls, 'visit_' + name, nonef)

def log_depart(cls, name):
    setattr(cls, 'depart_' + name, nonef)

[log_visit(Visitor, name) for name in ['document', 'section',
    'field_list']]
[log_depart(Visitor, name) for name in ['document', 'section', 'Text', 
    'new_page', 'pause', 'system_message', 'image', 'page_type',
    'template', 'output_to', 'field_list', 'field']]

class new_page(Node):
    '''new_page custom docutil node'''
    children = ()

from docutils.parsers.rst import Directive, directives
class NewPage(Directive):
    '''new_page custom directive.'''
    def run(self):
        return [new_page()]

class LeafNode(Node):
    children = ()

class pause(LeafNode):
    '''pause custom docutil node'''
    pass

class Pause(Directive):
    ''' pause current page's output, copy current page to next page, and
    continue after the pause directive. '''

    def run(self): 
        return [pause()]

class page_type(LeafNode):
    def __init__(self, type):
        self.type = type

class SetPageType(Directive):
    ''' set page type, like cover, normal... '''

    required_arguments = 1

    def run(self):
        return [page_type(self.arguments[0])]

class template(LeafNode):
    def __init__(self, template):
        self.template = template

class SetTemplate(Directive):
    '''set template class'''

    required_arguments = 1

    def run(self):
        return [template(self.arguments[0])]

class output_to(LeafNode):
    def __init__(self, output):
        self.output = output

class SetOutputTo(Directive):
    required_arguments = 1

    def run(self):
        return [output_to(self.arguments[0])]

directives.register_directive('new-page', NewPage)
directives.register_directive('pause', Pause)
directives.register_directive('page-type', SetPageType)
directives.register_directive('template', SetTemplate)
directives.register_directive('output-to', SetOutputTo)
del directives, Directive, NewPage, Pause, SetTemplate, SetOutputTo

class Settings(object):
    report_level = 2
    halt_level = 4
    warning_stream = '/dev/null'
    debug = False
    error_encoding = 'utf-8'
    error_encoding_error_handler = 'replace'
    tab_width = 4
    language_code = 'en'
    pep_references = 1
    rfc_references = 1
    strict_visitor = True
    id_prefix = 'id_'
    auto_id_prefix = 'aid_'

if __name__ == '__main__':
    from sys import argv
    from codecs import decode
    if len(argv) < 3:
        print 'Usage: %s [rst file] [output file]\n' % argv[0]
        exit(1)

    parser = docutils.parsers.rst.Parser()
    input = open(argv[1]).read()
    input = decode(input, 'utf-8')
    document = docutils.utils.new_document(argv[1], Settings())
    parser.parse(input, document)
    
    document.walkabout(Visitor(rstslide_template, document, argv[2]))
