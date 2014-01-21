# -*- coding: utf8 -*-
"""
barbarian.objects.factories.py
==============================

Entity builders.

"""
from barbarian.utils.data import merge_dicts
from barbarian.io.data import read_data_file
from barbarian.objects import entity


def _get_entity_data(data_dict, entity_name):
    """
    Return the queried entity's data, merging in any components properties
    defined in the __common__ item.

    Properties redefined by the entity will override the __common__ ones.
    """
    e_data = data_dict[entity_name]
    common = data_dict.get('__common__', {})

    res = merge_dicts(common, e_data)
    return common

def build_entity(entity_name, x=-1, y=-1, data_file='entities.json'):
    """ Dummy builder """

    # TODO: move to utils
    def import_from_path(path):
        """
            Import a class dynamically, given it's dotted path.
        """
        module_name, class_name = path.rsplit('.', 1)
        try:
            return getattr(__import__(module_name, fromlist=[class_name]), class_name)
        except AttributeError:
            raise ImportError('Unable to import %s' % path)

    data = read_data_file(data_file)
    e_data = _get_entity_data(data, entity_name)

    """
    Cls = import_from_path(e_data.pop('__entity_type__'))
    if Cls is None:
        logger.error('Entity type %s is not defined' % Cls.__name__)
        return  # TODO: better err handling
    """

    e_data.pop('__entity_type__')
    e = entity.Entity(entity_name, **e_data)
    if e.has_property('x'):
        e.set_property('x', x)
    if e.has_property('y'):
        e.set_property('y', y)
    return e


def build_player(level):
    """ Dummy player builder. """
    from barbarian.utils import rng
    px, py = rng.randrange(0, 80), rng.randrange(0, 40)
    while level.is_blocked(px, py):
        px, py = rng.randrange(0, 80), rng.randrange(0, 40)
    player = entity.Entity(
        entity_name='player',
        VisibleComponent=dict(char='@'),
        PositionComponent=dict(x=px, y=py),
        PlayerMobileComponent=dict(),
    )
    level.map.compute_fov(player.x, player.y)

    return player
