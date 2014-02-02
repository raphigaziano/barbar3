# -*- coding: utf8 -*-
"""
barbarian.barbar.py
===================

Game entry point.

"""
# pylint: disable=E1101
try:
    # TODO: check a DEBUG_MODE config var to decide whether we set the debugger
    # or not.
    from pudb import set_interrupt_handler
    set_interrupt_handler()
except ImportError:
    pass

from barbarian.gamestates import StateManager, InitState

state_manager = StateManager(InitState())

while not state_manager.is_done:

    state_manager.update()
