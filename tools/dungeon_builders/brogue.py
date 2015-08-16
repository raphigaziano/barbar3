import random

from barbarian.map import Map

from barbarian.io.settings import MAP_W, MAP_H
from barbarian.objects.factories import build_entity

# Most of this comes from either the rockpapershotgun overview
# @http://www.rockpapershotgun.com/2015/07/28/how-do-roguelikes-generate-levels/
# or from the brogue wiki
# @http://brogue.wikia.com/wiki/Level_Generation
# Ripoffs from the source are planned, too.

def make_map_brogue_cavern():

    """ Simple cavern """

    FLOOR_CHANCE = 55
    SMOOTHING_PASSES = 5

    my_map = Map(
        MAP_W, MAP_H,
        [build_entity('base_tile', data_file='mapobjs.json') for _ in range(MAP_W*MAP_H)]
    )

    def _make_floor(c):
        c.blocks = False
        c.blocks_sight = False

    def _make_wall(c):
        c.blocks = True
        c.blocks_sight = True

    def _is_floor(c):
        return not c.blocks

    for _, __, c in my_map:
        if random.randint(0, 100) < FLOOR_CHANCE:
            _make_floor(c)
        else:
            _make_wall(c)

    # Smoothing:
    # "In every round of smoothing,
    # every floor cell with fewer than four adjacent floor cells becomes a wall,
    # and every wall cell with six or more adjacent floor cells becomes a floor."
    for _ in range(SMOOTHING_PASSES):
        for x, y, c in my_map:
            neighbors = list(my_map.get_neighbors(x, y))
            if (_is_floor(c) and len(filter(_is_floor, neighbors)) < 4):
                _make_wall(c)
            elif (not _is_floor(c) and len(filter(_is_floor, neighbors)) >= 6):
                _make_floor(c)

    def isolate_one_room():
        # Grab the biggest open space and fill out the others
        already_flooded = set()
        num_cells_max = 0
        biggest_room = None
        for x, y, cell in my_map:
            if cell in already_flooded:
                continue
            room = list(my_map.floodfill(x, y, lambda c: not c.blocks))
            n = len(room)
            if n > num_cells_max:
                biggest_room = room
                num_cells_max = n
            for c in room:
                already_flooded.add(c)

        for x, y, cell in my_map:
            if cell not in biggest_room:
                _make_wall(cell)

    # isolate_one_room()

    my_map.init_fov_map()
    return my_map


def make_map_brogue_ripoff():
    pass
