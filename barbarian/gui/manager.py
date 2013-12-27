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
            'event_console': Console(0, 40, 80, 10),
            'debug_console': Console(5, 5, 70, 40),
        }
        self.widgets['debug_console'].visible = False
        # TODO: separate "static" and modals

    def __getitem__(self, key):
        return self.widgets[key]

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError as e:
            raise AttributeError()  # TODO: std err message

    def render(self):
        for name, w in self.widgets.items():
            renderer.dummy_draw_console(
                w, renderer.tcod_consoles[name], w.x, w.y
            )

    def show_widget(self, widget_name):
        self.widgets[widget_name].visible = True

    def hide_widget(self, widget_name):
        self.widgets[widget_name].visible = False

    def msg(self, msg, color):
        self._msg('event_console', msg, color)

    def debug(self, msg, color):
        self._msg('debug_console', msg, color)

    def _msg(self, widget_name, msg, color):
        self.widgets[widget_name].add_msg(msg, color)
