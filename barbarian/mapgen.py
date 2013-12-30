# -*- coding: utf8 -*-
"""
barbarian.mapgen.py

"""
from barbarian.map import Map
from barbarian.objects.mapobjects import MapTile
from barbarian.utils import rng, geometry


def make_map():

    """ For now, generator from the roguebasin tutorial. """

    MAP_WIDTH = 80
    MAP_HEIGHT = 40
    ROOM_MAX_SIZE = 10
    ROOM_MIN_SIZE = 6
    MAX_ROOMS = 30

    class Room(geometry.Rect):
        def __init__(self, x, y, w, h):
            self.x1 = x
            self.y1 = y
            self.x2 = x + w
            self.y2 = y + h

    def create_room(room):
        global my_map
        for x in range(room.x1+1, room.x2):
            for y in range(room.y1+1, room.y2):
                my_map.get_cell(x, y).blocks = False
                my_map.get_cell(x, y).blocks_sight = False

    def create_h_tunnel(x1, x2, y):
        global my_map
        for x in range(min(x1, x2), max(x1, x2) + 1):
            my_map.get_cell(x, y).blocks = False
            my_map.get_cell(x, y).blocks_sight = False

    def create_v_tunnel(y1, y2, x):
        global my_map
        for y in range(min(y1, y2), max(y1, y2) + 1):
            my_map.get_cell(x, y).blocks = False
            my_map.get_cell(x, y).blocks_sight = False

    rooms = []
    num_rooms = 0

    global my_map
    my_map = Map(
        MAP_WIDTH, MAP_HEIGHT,
        [MapTile(blocks=True) for _ in range(MAP_WIDTH * MAP_HEIGHT)]
    )

    for r in range(MAX_ROOMS):
        #random width and height
        w = rng.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE + 1)
        h = rng.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE + 1)
        #random position without going out of the boundaries of the map
        x = rng.randint(0, MAP_WIDTH - w - 1)
        y = rng.randint(0, MAP_HEIGHT - h - 1)

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
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                pass
            #     #this is the first room, where the player starts at
            #     player.x = new_x
            #     player.y = new_y
            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel

                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms-1].center()

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

    return my_map


