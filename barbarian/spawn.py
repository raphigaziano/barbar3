"""
Spawn logic.

"""
from collections import Counter
import logging
from pprint import pformat

from barbarian.raws import get_spawn_data, get_entity_data
from barbarian.entity import Entity
from barbarian.utils.rng import Rng
from barbarian.map import TileType

from barbarian.settings import MAX_SPAWNS


logger = logging.getLogger(__name__)


_entity_counter = Counter()


def spawn_entity(x, y, entity_data):
    """ Actual entity spawning. """
    if entity_data is None:
        return
    entity_data['pos'] = {'x': x, 'y': y}
    e =  Entity.from_dict(entity_data)
    try:
        _entity_counter[e.name] += 1
    except AttributeError:
        pass
    return e


def spawn_player(x, y):
    """ Shortcut. Spawn player at (x, y). """
    actor_data = get_entity_data('player', 'actors')
    return spawn_entity(x, y, actor_data)


def _spawn(container, entity):
    """
    Shortcut.

    Add entity to the passed container (either an `EntityContainer` or a
    `GridContainer`) if it is not None.

    """
    if entity is not None:
        container.add_e(entity)


def spawn_zone(level, zone_tiles, spawn_table):
    """
    Spawn entities for a single spawn zone (room or voronoi region).

    Zone tiles should be a list of cells from the desired spawn zone.

    """
    for _ in range(Rng.spawn.randint(0, MAX_SPAWNS)):
        entity_name = Rng.spawn.roll_table(spawn_table)
        for entity_cat in ('actors', 'items', 'props'):
            entity_data = get_entity_data(entity_name, entity_cat)
            if entity_data:
                x, y = Rng.spawn.choice(zone_tiles)
                container = getattr(level, entity_cat)
                _spawn(container, spawn_entity(x, y, entity_data))
                break
        else:
            logger.warning(
                'Could not load data for entity type %s', entity_name)


def spawn_stairs(level, x, y, entity_name):
    """
    Drop stairs (up or down) at coordinates (x, y).

    (Note, this would work for any prop).
    """
    data = get_entity_data(entity_name, 'props')
    _spawn(level.props, spawn_entity(x, y, data))


def spawn_door(level, x, y):
    """ Drop door at coordinates (x, y) if conditions are met. """
    if (
        level.map.in_bounds(x, y) and
        level.map[x, y] == TileType.FLOOR and
        not level.props[x,y] and
        # Some rooms share walls, which causes several doors to
        # be spawned an the same cells and causes shenanigans
        len(list(level.map.get_neighbors(
            x, y, cardinal_only=True,
            predicate=lambda _, __, c: c == TileType.FLOOR
        ))) == 2
    ):
        data = get_entity_data('door', 'props')
        _spawn(level.props, spawn_entity(x, y, data))


def spawn_level(level, spawn_zones):
    """ Spawn all the things on the passed in level. """

    _entity_counter.clear()

    ### Static props: Stairs ###

    spx, spy = level.start_pos
    spawn_stairs(level, spx, spy, 'stairs_up')
    # TMP: spawn stairs down right next to the start to ease
    # playtesting
    spawn_stairs(level, spx + 2, spy, 'stairs_down')

    epx, epy = level.exit_pos
    spawn_stairs(level, epx, epy, 'stairs_down')

    ### Static props: Doors ###

    for r in level.map.rooms:
        # Run along horizontal walls...
        for x in range(r.x - 1, r.x2 + 1):
            spawn_door(level, x, r.y - 1)     # North wall
            spawn_door(level, x, r.y2 + 1)    # South wall
        # Run along vertical walls...
        for y in range(r.y - 1, r.y2 + 1):
            spawn_door(level, r.x - 1, y)     # West wall
            spawn_door(level, r.x2 + 1, y)    # East wall

    ### Active entities: actors, items, props ###

    spawn_table = build_spawn_table(level)
    for z in spawn_zones:
        spawn_zone(level, z, spawn_table)

    for entity_name, n in _entity_counter.items():
        logger.debug(
            'Spawned entities for depth %d: %d %s', level.depth, n, entity_name)


def build_spawn_table(level):
    """
    Build the spawn table and return it.

    Weights will be adjusted according to the current depth according to
    the forumla (weight = entity.weight + (depth * entity.depth_mod))

    """
    def _adjust_entity_weight(entity):
        return max(
            0,
            entity['weight'] + (level.depth * entity.get('depth_mod', 0))
        )

    sd = get_spawn_data()
    st =  [(_adjust_entity_weight(e), e['name']) for e in sd]
    logger.debug('Built spawn_table:\n%s', pformat(st))
    return st
