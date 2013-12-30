# -*- coding: utf8 -*-
"""
barbarian.gui.uicomponents.py
=============================

Lib-agnostic UI Components.

See renderers.gui modules for GUI displaying.
"""


class Line(object):

    """
    A simple line of text to be displayed.

    Store the text itself along with a color object (the actual type of this
    object will depend on the current renderer).

    """

    def __init__(self, txt, col='default'):
        self.txt = txt
        self.col = col

    def __str__(self):
        return self.txt

