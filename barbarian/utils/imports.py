# -*- coding: utf8 -*-
"""
barbarian.utils.imports
=======================

Helpers for dynamic imports.

"""


def import_from_path(path):
    """ Import a class or module dynamically, given it's dotted path. """
    path, obj_name = path.rsplit('.', 1)
    try:
        return getattr(__import__(path, fromlist=[obj_name]), obj_name)
    except AttributeError:
        raise ImportError('Unable to import %s' % path)


