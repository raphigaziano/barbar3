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


def spawn_zone(level, zone_tiles, spawn_table, n_spawns):
    """
    Spawn `n_spawns` entities for a single spawn zone (room or voronoi region).

    Zone tiles should be a list of cells from the desired spawn zone.

    """
    tiles = list(zone_tiles)

    def __spawn_entity(entity_data, n):
        # Entities can be "grouped" without defining a subtable
        # (simply spawn n of the same entity)
        for _ in range(n):
            while tiles:
                x, y = Rng.spawn.choice(tiles)
                if level.is_blocked(x, y):
                    # Invalid cell; will be unavailable to later
                    # choices for this zone.
                    tiles.remove((x, y))
                    continue
                container = getattr(level, entity_cat)
                _spawn(container, spawn_entity(x, y, entity_data))
                break

    for _ in range(n_spawns):
        entity_spawn_data = Rng.spawn.roll_table(spawn_table)
        # Group item: call spawn_zone recursively on the defined subtable
        if subtable := entity_spawn_data.get('subtable', []):
            sub_spawn_table = build_spawn_table(
                level, subtable, adjust_weights=False)
            n_sub_spawns = Rng.try_roll_dice_str(entity_spawn_data.get('n', 1))
            spawn_zone(level, tiles, sub_spawn_table, n_sub_spawns)
        # Regular entity
        else:
            for entity_cat in ('actors', 'items', 'props'):
                entity_data = get_entity_data(entity_spawn_data['name'], entity_cat)
                if entity_data:
                    __spawn_entity(
                        entity_data,
                        Rng.try_roll_dice_str(entity_spawn_data.get('n', 1))
                    )
                    break
            else:
                logger.warning(
                    'Could not load data for entity type %s', entity_spawn_data['name'])


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

    spawn_table = build_spawn_table(level, get_spawn_data())
    for z in spawn_zones:
        spawn_zone(level, z, spawn_table, Rng.randint(0, MAX_SPAWNS))

    for entity_name, n in _entity_counter.items():
        logger.debug(
            'Spawned entities for depth %d: %d %s', level.depth, n, entity_name)


def build_spawn_table(level, spawn_data, adjust_weights=True):
    """
    Build the spawn table from the passed in `spawn_data` and return it.

    If `adjust_weights` is True (default), item weights will be adjusted 
    according to the current depth:
    weight = entity.weight + (depth * entity.depth_mod)

    """
    def _adjust_entity_weight(entity):
        if not adjust_weights:
            return entity['weight']
        return max(
            0,
            entity['weight'] + (level.depth * entity.get('depth_mod', 0))
        )

    st =  [(_adjust_entity_weight(e), e) for e in spawn_data]

    logger.debug('Built spawn_table:\n%s', pformat(st))
    return st
