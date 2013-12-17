# -*- coding: utf8 -*-
"""
barbarian.barbar.py
===================

Game entry point.

"""
# pylint: disable=E1101

from renderers import renderer

import map
m = map.Map(80, 40, map.dummy_generator)

from utils import rng
px, py = rng.randrange(0, 80), rng.randrange(0, 40)
while m.get_cell(px, py):
    px, py = rng.randrange(0, 80), rng.randrange(0, 40)

while True:
    renderer.dummy_draw_map(m)
    renderer.dummy_draw_player(px, py)

    renderer.flush()
