# -*- coding: utf8 -*-
"""
barbarian.mapgen.py

"""
from barbarian.map import Map
from barbarian.utils import rng, geometry

from barbarian.io.settings import MAP_W, MAP_H
from barbarian.objects.factories import build_entity


def make_map():

    """ For now, generator from the roguebasin tutorial. """

    ROOM_MAX_SIZE = 10
    ROOM_MIN_SIZE = 6
    MAX_ROOMS = 30

    class Room(geometry.Rect):
        pass

    my_map = Map(
        MAP_W, MAP_H,
        # [MapTile(**{'SolidComponent': {'blocks': True}}) for _ in range(MAP_W * MAP_H)]
        [build_entity('base_tile', data_file='mapobjs.json')
         for _ in range(MAP_W * MAP_H)]
    )

    def create_room(room):
        for x in range(room.x+1, room.x2):
            for y in range(room.y+1, room.y2):
                my_map.get_cell(x, y).blocks = False
                my_map.get_cell(x, y).blocks_sight = False

    def create_h_tunnel(x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            my_map.get_cell(x, y).blocks = False
            my_map.get_cell(x, y).blocks_sight = False

    def create_v_tunnel(y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            my_map.get_cell(x, y).blocks = False
            my_map.get_cell(x, y).blocks_sight = False

    rooms = []
    num_rooms = 0

    for _ in range(MAX_ROOMS):
        #random width and height
        w = rng.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE + 1)
        h = rng.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE + 1)
        #random position without going out of the boundaries of the map
        x = rng.randint(0, MAP_W - w - 1)
        y = rng.randint(0, MAP_H - h - 1)

        #"Room" class makes rectangles easier to work with
        new_room = Room(x, y, w, h)

        #run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            #this means there are no intersections, so this room is valid

            #"paint" it to the map's tiles
            create_room(new_room)

            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center

            if num_rooms > 1:
                #all rooms after the first:
                #connect it to the previous room with a tunnel

                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms-1].center

                #draw a coin (random number that is either 0 or 1)
                if rng.coin_flip():
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1

    my_map.init_fov_map()
    return my_map


