# -*- coding: utf8 -*-
"""
barbarian.gui.manager.py
========================

"""
from barbarian.gui.widgets import Console
from barbarian.renderers import renderer


class GUIManager(object):
    """
    Container & Manager for all the GUI widgets.

    """
    def __init__(self):
        self.widgets = {
            'event_console': (0, 40, Console(80, 10)),
            'debug_console': (5, 5,  Console(70, 40)),
        }
        self.widgets['debug_console'][2].visible = False

    def __getitem__(self, key):
        return self.widgets[key][2]

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError as e:
            raise AttributeError()  # TODO: std err message

    def show_widget(self, widget_name):
        self.widgets[widget_name][2].visible = True

    def hide_widget(self, widget_name):
        self.widgets[widget_name][2].visible = False

    def draw(self):
        for _, (x, y, w) in self.widgets.items():
            if w.visible:
                renderer.dummy_draw_console(w, x, y)

    def msg(self, msg):
        self._msg('event_console', msg)

    def debug(self, msg):
        self._msg('debug_console', msg)

    def _msg(self, widget_name, msg):
        self.widgets[widget_name][2].add_msg(msg)
