# -*- coding: utf8 -*-
"""
barbarian.utils.settings.py
===========================

Simple settings collecter.

TODO: Plan a way to have default settings (somewhere) + user overrides

"""
import os, sys


class InvalidSetting(ValueError, Exception):
    pass

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
    setting_name,
    py_type=None,
    default=None,
    required=False,
    settings_file=SETTINGS_PATH
):
    if not _SETTINGS_DICT:
        _read_settings(settings_file)
    s = _SETTINGS_DICT.get(setting_name)
    if s is None:
        if default:
            _SETTINGS_DICT[setting_name] = default
            return default
        if required:
            raise InvalidSetting("Missing required setting: %s" % setting_name)
    # TODO: Callback validators ?
    if py_type is not None and py_type is not type(s):
        raise InvalidSetting(
            "Invalid setting: %s must be of type %s" % (setting_name, py_type)
        )
    return s


LIMIT_FPS = _get_setting('LIMIT_FPS', py_type=int)
SCREEN_W = _get_setting('SCREEN_W', py_type=int, required=True)
SCREEN_H = _get_setting('SCREEN_H', py_type=int, required=True)

MAP_W = _get_setting('MAP_W', py_type=int, required=True)
MAP_H = _get_setting('MAP_H', py_type=int, required=True)

RENDERER = _get_setting('RENDERER', py_type=str, default='libtcod')

ASSETS_ROOT = _get_setting(
    'ASSETS_ROOT', py_type=str,
    default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'assets'
    ),
    required=True
)

