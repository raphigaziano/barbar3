# -*- coding: utf8 -*-
"""
barbarian.gui.widgets.py
========================

Lib-agnostic GUI Widgets.
These will hold needed state information, but won't bother with rendering
themselves.

See renderers.gui modules for GUI displaying.
"""
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
    def __init__(self, width, height, title=None, children=None):

        # Those values should be handled by the renderer:
        #
        # forecolor=tcod.white, backcolor=tcod.black,
        # framed=True, frame_color=tcod.white,
        # forealpha=1, backalpha=0.6,

        self.w = width
        self.h = height
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
        #self.dirty = True

        self.children = children or []

class Console(Widget):
    def __init__(self, *args, **kwargs):
        super(Console, self).__init__(*args, **kwargs)
        self.msgs = []

    def add_msg(self, msg):
        self.msgs.append(msg)
