# -*- coding: utf8 -*-
"""
barbarian.input.libtcod.py
==========================

"""
from barbarian import libtcodpy as libtcod
from barbarian.input.utils import read_lib_keymap


_KEYMAP = read_lib_keymap('input_settings/libtcod.json', libtcod)

def collect_keypresses():
    # DUMMY
    key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
    # TCOD_KEY fields:
    # vk, c, pressed,
    # lalt, lctrl, ralt, rctrl, shift
    if key.pressed:
        if key.vk == libtcod.KEY_CHAR:
            return chr(key.c)
        return _KEYMAP.get(key.vk)
    return None
