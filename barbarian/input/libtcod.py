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
    if key.pressed:
        if key.vk == libtcod.KEY_CHAR:
            pressed = chr(key.c)
        else:
            pressed = _KEYMAP[key.vk]
        key_seq = []
        if key.lctrl or key.rctrl:
            key_seq.append('<ctrl>')
        if key.lalt or key.ralt:
            key_seq.append('<alt>')
        if key.shift:
            key_seq.append('<shift>')
        key_seq.append(pressed)
        return '-'.join(key_seq)
    return None
