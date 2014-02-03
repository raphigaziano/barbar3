# -*- coding: utf8 -*-
"""
barbarian.input.utils.py
========================

Common helpers for input reading.

"""
from barbarian.io.data import read_data_file


def read_lib_keymap(def_file_path, lib_obj):
    input_data = read_data_file(def_file_path)
    return {
        getattr(lib_obj, v): k
        for k, v in input_data['keyboard']['keys'].items()
    }


def read_keybindings(def_file_path):
    input_data = read_data_file(def_file_path)
    return {
        state: {
            tuple(keys): action for action, keys in keybindings.items()
        }
        for state, keybindings in input_data.items()
    }
