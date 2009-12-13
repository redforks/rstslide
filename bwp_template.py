# -*- coding: utf-8 -*-
from __future__ import absolute_import

import cairo

from rstslide_template import PageType, default, cover

class default(default):
    def render_background(self, visitor):
        ctx, fields = visitor.ctx, visitor.fields
        liner = cairo.LinearGradient(0, 0, 800, 0)
        liner.add_color_stop_rgb(0, 0.7539, 0.7539, 0.7539)
        liner.add_color_stop_rgb(0.5, 0.7227, 0.7227, 0.7227)
        liner.add_color_stop_rgb(1, 1, 1, 1)
        ctx.set_source(liner)
        ctx.rectangle(0, 0, 800, 70)
        ctx.fill()

        ctx.set_source_rgb(0.7227, 0.7227, 0.7227)
        ctx.rectangle(0, 570, 800, 600)
        ctx.fill()

        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(80, 590)
        ctx.set_font_size(12)
        ctx.show_text(fields.get('componey', 'set componey field'))

        ctx.select_font_face('Droid Serif', cairo.FONT_SLANT_NORMAL,
                cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(42)
        ctx.move_to(680, 50)
        ctx.scale(1, 0.9)
        ctx.set_source_rgb(0.28515625, 0.57421875, 0.62109375)
        ctx.show_text('BWP')

class cover(cover):
    title_pos = 350, 300
    title_color = 1.0, 1.0, 1.0

    def render_background(self, visitor):
        ctx, fields = visitor.ctx, visitor.fields
        ctx.set_source_rgb(0.46666667, 0.717647, 0.90588)
        ctx.rectangle(0, 0, 280, 240)
        ctx.fill()

        ctx.set_source_rgb(0, 0.2, 0.4)
        ctx.rectangle(0, 240, 800, 10)
        ctx.rectangle(320, 240, 800-320, 100)
        ctx.fill()

        img = cairo.ImageSurface.create_from_png('title.png')
        ctx.set_source_surface(img, 280, 0)
        ctx.paint()

        ctx.move_to(250, 550)
        ctx.set_source_rgb(0, 0.4, 0.4)
        ctx.set_font_size(24)
        ctx.show_text(fields.get('componey', 'set componey field'))

        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(50, 80, 160, 60)
        ctx.fill()

        ctx.select_font_face('Droid Serif', cairo.FONT_SLANT_NORMAL,
                cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(60)
        ctx.move_to(60, 129)
        ctx.scale(1, 0.9)
        ctx.set_source_rgb(0.28515625, 0.57421875, 0.62109375)
        ctx.show_text('BWP')
