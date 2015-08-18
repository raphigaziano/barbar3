import random

from barbarian.map import Map

from barbarian.io.settings import MAP_W, MAP_H
from barbarian.objects.factories import build_entity


def make_map_cellular_automata_basic():

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


def make_map_cellular_automata_full_room():

    """
    Basically the same as borgue_cavern, but try to ensure the cavern will fill
    most of the available space.

    """

    FLOOR_CHANCE = 55
    SMOOTHING_PASSES = random.randint(2, 8)
    print('Smoothing passes: ', SMOOTHING_PASSES)

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

    # This is the difference with the regular brogue_caren algorithm:
    # We significantly bump up the chances for open starting tiles along the
    # center of the map.
    #
    # We alternate between to method for determining which tiles will have their
    # floor chance bumped (chosen randomly on each run of the function for
    # demo/testing purposes):
    #
    # - A cross in the middle of the map (basically, drawing two 3 perpendicular,
    #   3 tile wide lines along the middle x and y axis)
    # - A rectangle right in the middle of the map.
    #
    # Cross pattern seems to need at least of +30 bump to be effective,
    # while Rect gets away with as little as 10 (although 30 looks fine as
    # well: basically, the less bump, the more random the final shape looks.
    # +30 is basically an irregular, "eroded" rectangle, while +10 gets the
    # organic feel back while still looking like a single room.
    # To sump up: rect feels more like a room (the more twisted/organic the less
    # the chance bump), while cross feels more like winding passages.

    middle_x, middle_y = MAP_W / 2, MAP_H / 2
    cross_offset_x = MAP_W / 4
    cross_offset_y = MAP_H / 4

    def _central_cross_floor_chances(x, y):
        if (
            (x in (middle_x-1, middle_x, middle_x + 1) and
             y > cross_offset_y and y < MAP_H-cross_offset_y) or
            (y in (middle_y-1, middle_y, middle_y+1) and
             x > cross_offset_x and x < MAP_W-cross_offset_x)
        ):
            return FLOOR_CHANCE + 30
        else:
            return FLOOR_CHANCE

    _central_chance_bump = random.randint(10, 31)
    print 'central chance bump: ', _central_chance_bump
    def _central_rect_floor_chances(x, y):
        if (
            x > cross_offset_x and x < MAP_W-cross_offset_x and
            y > cross_offset_y and y < MAP_H-cross_offset_y
        ):
            return FLOOR_CHANCE + _central_chance_bump
        else:
            return FLOOR_CHANCE

    central_chance_modifier = random.choice((
        _central_cross_floor_chances, _central_rect_floor_chances))
    print 'chance modifier: ', central_chance_modifier

    for x, y, c in my_map:

        floor_chance = central_chance_modifier(x, y)

        # Closing off the map edges to reduce chances of large unclosed sections.
        if (x <= 1 or x >= MAP_W-2 or y <= 1 or y >= MAP_H-2):
            _make_wall(c)
        elif random.randint(0, 100) < floor_chance:
            _make_floor(c)
        else:
            _make_wall(c)

    # - my_map.init_fov_map()
    # - return my_map

    for _ in range(SMOOTHING_PASSES):
        for x, y, c in my_map:
            neighbors = list(my_map.get_neighbors(x, y))
            if (_is_floor(c) and len(filter(_is_floor, neighbors)) < 4):
                _make_wall(c)
            elif (not _is_floor(c) and len(filter(_is_floor, neighbors)) >= 6):
                _make_floor(c)

    my_map.init_fov_map()
    return my_map
