#! /usr/bin/env python
#-*- coding:utf-8 -*-
"""
barbarian.gui.widgets.py
========================

Lib-agnostic GUI Widgets.
These will hold needed state information, but won't bother with rendering
themselves.

See renderers.gui modules for GUI displaying.
"""

#import textwrap

# from libtGUI.components import *

#########################
##  Base Widget Class  ##
#########################

class Widget:
    """
    Base Widget class, from which all other widgets inherit.

    Hold basic attributes common to all widget like position, whether it should
    be shown, etc...
    """
    def __init__(self, width, height, title=None, children=None)

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
        if self.title and len(self.title) > self.w:
            # +4 => 2 more cells on each side
            self.w = len(self.title) + 4

        self.visible = True
        #self.dirty = True

        self.children = children or []


    # TODO: move to renderers
    def display(self, x, y, blit_on=0):
        """
        Blits the widget to the console passed as parameter (defaults to
        the root console), with its top-left corner at the specified
        x:y position.
        This is the bare minimum any widget will have to do to draw
        itself.
        """
        if not self.visible: return
        if self.framed:
            # draw an old school looking frame around the window \o/
            tcod.console_set_foreground_color(self.con, self.frame_color)
            tcod.console_print_frame(self.con, 0, 0, self.w, self.h,
                                     False, tcod.BKGND_NONE, self.title)
        # blit any children on the widget's console
        for child in self.children:
            child.display()
        # Blit self
        tcod.console_blit(self.con, 0, 0, self.w, self.h, blit_on, x, y,
                          self.forealpha, self.backalpha)

        #tcod.console_flush()

