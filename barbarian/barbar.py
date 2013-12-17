# -*- coding: utf8 -*-
"""
barbarian.barbar.py
===================

Game entry point.

"""
# pylint: disable=E1101

from gamestates import StateManager, DungeonState
from renderers import renderer

state_manager = StateManager()
state_manager.push(DungeonState())

renderer.init()

while True:

    state_manager.update()
    cs = state_manager.current_state
    cs.process_input()

    renderer.dummy_draw_map(cs.m)
    renderer.dummy_draw_player(cs.px, cs.py)

    renderer.flush()
