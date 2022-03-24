"""
Read and process raw files.

"""
import os
import logging
from copy import deepcopy

import yaml

from barbarian.utils.data import merge_dicts

from barbarian.settings import RAWS_ROOT


logger = logging.getLogger(__name__)

_entity_tables = {
    'actors': {},
    'props': {},
    'items': {},
    'spawn': [],
}


def load_raws():
    """
    Load all raw files:
    - actors, items & props definitions
    - entity spawn table.

    """
    for table_key in _entity_tables:
        fname = f'entities/{table_key}.yaml'
        load_raw_table(table_key, fname)


def load_raw_table(table_key, raw_file_name):
    """ Load individual data from raw file. """
    raw_path = os.path.join(RAWS_ROOT, raw_file_name)
    logger.debug('loading %s entities from disk', table_key)
    with open(raw_path, 'r', encoding='utf-8') as f:
        _entity_tables[table_key] = yaml.safe_load(f.read())


def get_spawn_data():
    """ Return the spawn data, loading it if needed from `spawn.yaml`. """
    if not _entity_tables['spawn']:
        load_raws()

    return _entity_tables['spawn']


def get_entity_data(entity_name, table_key):
    """
    Retrieve entity data from the appropriate table, populating said
    table from a raw file if it's empty.

    """
    if not table_key in _entity_tables:
        logger.warning('Invalid entity table key: %s', table_key)
        return

    if not _entity_tables[table_key]:
        load_raws()

    table = _entity_tables[table_key]

    try:
        entity_data = deepcopy(table[entity_name])
    except KeyError:
        return

    parent = entity_data.pop('_parent', None)
    if parent:
        # Recursively merge parent's data into the current entity
        # to allow inheriting data in the raws
        parent_data = get_entity_data(parent, table_key)
        entity_data = merge_dicts(entity_data, parent_data)

    return entity_data
