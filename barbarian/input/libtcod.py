# -*- coding: utf8 -*-
"""
barbarian.input.libtcod.py
==========================

"""
from barbarian import libtcodpy as libtcod

def collect():
    # DUMMY
    return libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
