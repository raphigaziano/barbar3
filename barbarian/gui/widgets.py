# -*- coding: utf8 -*-
"""
barbarian.gui.widgets.py
========================

Lib-agnostic GUI Widgets.
These will hold needed state information, but won't bother with rendering
themselves.

See renderers.gui modules for GUI displaying.
"""
from barbarian.renderers import renderer
from barbarian.gui.uicomponents import Line
# from libtGUI.components import *

#########################
##  Base Widget Class  ##
#########################

class Widget(object):
    """
    Base Widget class, from which all other widgets inherit.

    Hold basic attributes common to all widget like position, whether it should
    be shown, etc...

    """
    def __init__(self, x, y, width, height, title=None, children=None):

        # Those values should be handled by the renderer:
        #
        # forecolor=tcod.white, backcolor=tcod.black,
        # framed=True, frame_color=tcod.white,
        # forealpha=1, backalpha=0.6,

        self.x, self.y = x, y
        self.w, self.h = width, height
        self.title = title
        # self.framed = framed
        # if self.framed:
        #     self.frame_color = frame_color
        #     # adjust dimension to include the frame:
        #     self.w += 1
        #     self.h += 1
        # if self.title and len(self.title) > self.w:
        #     # +4 => 2 more cells on each side
        #     self.w = len(self.title) + 4

        self.visible = True
        self.dirty = True

        self.children = children or []

    def render(self):
        if self.visible:
            renderer.dummy_draw_console(self, self.x, self.y)
            for c in self.children:
                c.render()

    def process_input(self, key):
        """ Stub Method. """
        pass

class Console(Widget):

    """ Scrolling (or rather, offseted) Messages Container. """

    def __init__(self, *args, **kwargs):
        super(Console, self).__init__(*args, **kwargs)
        self.msgs = []
        self._offset = 0

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, v):
        """ Disallow setting offset below zero. """
        if v <= 0:
            return
        if v >= len(self.msgs):# - self.h:
            return
        self._offset = v

    @property
    def last_msgs(self, n=None):
        if n is None:
            n = self.h
        start = -(n + self._offset)
        # if abs(start) > self.h:
        #     start += self.h
        end = -self._offset if self._offset > 0 else -1
        return self.msgs[start:end]

    def write(self, msg, col='default'):
        self.msgs.append(Line(msg, col))
        # if len(self.msgs) >= self.h:
            # self.offset += 1
        # self.dirty = True

    def process_input(self, key):
        from barbarian import libtcodpy as tcod
        if key.vk in (tcod.KEY_UP, tcod.KEY_KP8):
            self.offset += 1
        elif key.vk in (tcod.KEY_DOWN, tcod.KEY_KP2):
            self.offset -= 1
        if key.vk == tcod.KEY_ESCAPE or key.c == ord('d'):
            self.visible = False
