# -*- coding: utf8 -*-
"""
barbarian.io.data.py
====================

Data files (json) reading helpers.

"""
import os
import json


DATA_ROOT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'data'
)

def read_data(f):
    """
    Return a dict read from the passed json file object.

    """
    # Convert all single quotes to double ones, or the json parser
    # blows up.
    raw_data = f.read().replace('\'', '"')
    return json.loads(raw_data)

def read_data_file(path):
    """ Open the json file locaed at `path` and return its content as a dict. """
    with open(os.path.join(DATA_ROOT_PATH, path)) as f:
        return read_data(f)
