# -*- coding: utf8 -*-
"""
barbarian.renderers.litbcod.gfxdata
===================================

Rendering specific data structures.

"""
from barbarian import libtcodpy as libtcod
from barbarian.io.data import read_data_file


# THIS IS POOPIN FUGLY BUT POOP
class RenderData(object):

    COLOR_MAP = {}

    def __init__(self, **kwargs):
        self._read_colors('graphics/base_colors.json')
        self.color = self._get_color(kwargs['color'])

    def _read_colors(self, col_file):
        if self.COLOR_MAP:
            return
        col_data = read_data_file(col_file)
        for col_name, col_val in col_data.items():
            self.COLOR_MAP[col_name] = self._get_color_object(col_val)

    def _get_color_object(self, col_val):
        if col_val.startswith('#'):     # TODO: is_hexa or somesuch method
            return libtcod.Color(*self._hex_to_rgb(col_val))
        r, g, b = map(int, col_val.split(','))
        return libtcod.Color(r, g, b)

    def _get_color(self, col_name):
        try:
            return self.COLOR_MAP[col_name]
        except KeyError:
            return self._get_color_object(col_name)

    # Stack Overflow: http://stackoverflow.com/a/214657
    @staticmethod
    def _hex_to_rgb(value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))

    @staticmethod
    def _rgb_to_hex(rgb):
        return '#%02x%02x%02x' % rgb
