# -*- coding: utf-8 -*-
from __future__ import absolute_import

class PageType(object):
    margin_left = 10
    margin_right = 760

    title_pos = margin_left, 47
    title_font_size = 40
    title_color = 0, 0, 0

    font_size = 16
    font_face = 'Droid Sans Fallback'

    block_quote_font_size = 10
    block_quote_margin_left = 50
    block_quote_margin_right = 700
    block_quote_font_face = font_face

    monospace_font_face = 'Droid Sans Mono'

    content_pos = margin_left, 90
    
    para_line_height = 2
    para_after_height = 5

    sub_list_indent = 10

    _output_map = {
        'left': (margin_left, content_pos[1], 380, 500),
        'right': (400, content_pos[1], 380, 500),
    }

    def render_background(self, ctx, fields):
        pass

    def get_output_rect(self, output_name):
        return self._output_map[output_name]

class default(PageType):
    def render_background(self, ctx, fields):
        pass

class cover(PageType):
    title_pos = 30, 200

    def render_background(self, ctx, fields):
        pass
