# -*- coding: utf8 -*-
"""
barbarian.input.common
======================

Common interface to various libraries to handle input events.

"""
import json

from barbarian.io import settings
from barbarian.utils.imports import import_from_path
from barbarian.input.utils import read_keybindings

INPUT_LIB = import_from_path('barbarian.input.%s' % settings.RENDERER)

_KEYBINDINGS = read_keybindings('keymap.json')


def collect_keypresses():
    """
    Simply grab the currently pressed key and return its internal keycode.

    """
    return INPUT_LIB.collect_keypresses()


def check_keypress(key, current_keymap):
    """ Return the action bound to `key` in `current_keymap` or None. """
    for keys, action in _KEYBINDINGS[current_keymap].items():
        if key in keys:
            return action
    return None


def collect_action(current_keymap):
    """ Check if any keypress resulted in a defined action. """
    return check_keypress(collect_keypresses(), current_keymap)

