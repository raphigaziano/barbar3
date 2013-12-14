# -*- coding: utf8 -*-
"""
barbarian.utils.settings.py
===========================

Simple settings collecter.

TODO: Plan a way to have default settings (somewhere) + user overrides

"""
import os, sys

SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'data', 'settings'
)

_SETTINGS_DICT = {}

def _read_settings(settings_file=SETTINGS_PATH):

    with open(settings_file, 'r') as sf:
        for l in sf.readlines():
            if l.isspace() or l.startswith('#'):
                continue
            k, v = l.split('=')
            k, v = k.strip(), v.strip()
            _SETTINGS_DICT[k] = eval(v)     # TODO: secure this

def _get_setting(
    setting_name, default=None, required=False, settings_file=SETTINGS_PATH
):
    if not _SETTINGS_DICT:
        _read_settings(settings_file)
    s = _SETTINGS_DICT.get(setting_name)
    if s is None:
        if default:
            s = _SETTINGS_DICT[setting_name] = default
            return s
        if required:
            raise Exception("ONOES")    # TODO: specialized exc and explicit msg
    # TODO: type checking
    return s

LIMIT_FPS = _get_setting('LIMIT_FPS')
SCREEN_W = _get_setting('SCREEN_W', required=True)
SCREEN_H = _get_setting('SCREEN_H', required=True)

RENDERER = _get_setting('RENDERER', default='libtcod')
