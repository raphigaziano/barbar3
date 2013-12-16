# -*- coding: utf8 -*-
"""
barbarian.barbar.py
===================

Game entry point.

"""
# pylint: disable=E1101

from renderers import renderer

import map
m = map.Map(map.dummy_generator)
while True:
    renderer.dummy_draw_map(m)
