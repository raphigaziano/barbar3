# -*- coding: utf8 -*-
"""
barbarian.barbar.py
===================

Game entry point.

"""
# pylint: disable=E1101

from gamestates import StateManager, InitState

state_manager = StateManager(InitState())

while not state_manager.is_done:

    state_manager.update()
