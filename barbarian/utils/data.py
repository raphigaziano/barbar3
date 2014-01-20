# -*- coding: utf8 -*-
"""
barbarian.utils.data.py
=======================

Helpers to manage various data structures.

"""

# from http://code.activestate.com/recipes/499335-recursively-update-a-dictionary-without-hitting-py/
def merge_dicts(dst, src):
    """ Recursively merge src dictionnary into dst. """
    stack = [(dst, src)]
    while stack:
        current_dst, current_src = stack.pop()
        for key in current_src:
            if key not in current_dst:
                current_dst[key] = current_src[key]
            else:
                if (isinstance(current_src[key], dict) and
                    isinstance(current_dst[key], dict)
                ):
                    stack.append((current_dst[key], current_src[key]))
                else:
                    current_dst[key] = current_src[key]
    return dst
