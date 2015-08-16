from barbarian.map import Map
from barbarian.utils import rng, geometry

from barbarian.io.settings import MAP_W, MAP_H
from barbarian.objects.factories import build_entity


def make_map_basic_libtcod_tut():
    """ Basic generator from the roguebasin tutorial """

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
                my_map[x, y].blocks = False
                my_map[x, y].blocks_sight = False

    def create_h_tunnel(x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            my_map[x, y].blocks = False
            my_map[x, y].blocks_sight = False

    def create_v_tunnel(y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            my_map[x, y].blocks = False
            my_map[x, y].blocks_sight = False

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


import random
import itertools

def make_map_roguebasin_exemple_1():
    """ From some roeguebasin article TODO: find ou twhich one) """
    def _AStar(start, goal):
        def heuristic(a, b):
            ax, ay = a
            bx, by = b
            return abs(ax - bx) + abs(ay - by)

        def reconstructPath(n):
            if n == start:
                return [n]
            return reconstructPath(cameFrom[n]) + [n]

        def neighbors(n):
            x, y = n
            return (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)

        closed = set()
        open = set()
        open.add(start)
        cameFrom = {}
        gScore = {start: 0}
        fScore = {start: heuristic(start, goal)}

        while open:
            current = None
            for i in open:
                if current is None or fScore[i] < fScore[current]:
                    current = i

            if current == goal:
                return reconstructPath(goal)

            open.remove(current)
            closed.add(current)

            for neighbor in neighbors(current):
                if neighbor in closed:
                    continue
                g = gScore[current] + 1

                if neighbor not in open or g < gScore[neighbor]:
                    cameFrom[neighbor] = current
                    gScore[neighbor] = g
                    fScore[neighbor] = gScore[neighbor] + heuristic(neighbor, goal)
                    if neighbor not in open:
                        open.add(neighbor)
        return ()


    def generate(cellsX, cellsY, cellSize=5):
        # 1. Divide the map into a grid of evenly sized cells.

        class Cell(object):
            def __init__(self, x, y, id):
                self.x = x
                self.y = y
                self.id = id
                self.connected = False
                self.connectedTo = []
                self.room = None

            def connect(self, other):
                self.connectedTo.append(other)
                other.connectedTo.append(self)
                self.connected = True
                other.connected = True

        cells = {}
        for y in range(cellsY):
            for x in range(cellsX):
                c = Cell(x, y, len(cells))
                cells[(c.x, c.y)] = c

        # 2. Pick a random cell as the current cell and mark it as connected.
        current = lastCell = firstCell = random.choice(cells.values())
        current.connected = True

        # 3. While the current cell has unconnected neighbor cells:
        def getNeighborCells(cell):
            for x, y in ((-1, 0), (0, -1), (1, 0), (0, 1)):
                try:
                    yield cells[(cell.x + x, cell.y + y)]
                except KeyError:
                    continue

        while True:
            unconnected = filter(lambda x: not x.connected, getNeighborCells(current))
            if not unconnected:
                break

            # 3a. Connect to one of them.
            neighbor = random.choice(unconnected)
            current.connect(neighbor)

            # 3b. Make that cell the current cell.
            current = lastCell = neighbor

        # 4. While there are unconnected cells:
        while filter(lambda x: not x.connected, cells.values()):
            # 4a. Pick a random connected cell with unconnected neighbors and connect to one of them.
            candidates = []
            for cell in filter(lambda x: x.connected, cells.values()):
                neighbors = filter(lambda x: not x.connected, getNeighborCells(cell))
                if not neighbors:
                    continue
                candidates.append((cell, neighbors))
            cell, neighbors = random.choice(candidates)
            cell.connect(random.choice(neighbors))

        # 5. Pick 0 or more pairs of adjacent cells that are not connected and connect them.
        extraConnections = random.randint((cellsX + cellsY) / 4, int((cellsX + cellsY) / 1.2))
        maxRetries = 10
        while extraConnections > 0 and maxRetries > 0:
            cell = random.choice(cells.values())
            neighbor = random.choice(list(getNeighborCells(cell)))
            if cell in neighbor.connectedTo:
                maxRetries -= 1
                continue
            cell.connect(neighbor)
            extraConnections -= 1

        # 6. Within each cell, create a room of random shape
        rooms = []
        for cell in cells.values():
            width = random.randint(3, cellSize - 2)
            height = random.randint(3, cellSize - 2)
            x = (cell.x * cellSize) + random.randint(1, cellSize - width - 1)
            y = (cell.y * cellSize) + random.randint(1, cellSize - height - 1)
            floorTiles = []
            for i in range(width):
                for j in range(height):
                    floorTiles.append((x + i, y + j))
            cell.room = floorTiles
            rooms.append(floorTiles)

        # 7. For each connection between two cells:
        connections = {}
        for c in cells.values():
            for other in c.connectedTo:
                connections[tuple(sorted((c.id, other.id)))] = (c.room, other.room)
        for a, b in connections.values():
            # 7a. Create a random corridor between the rooms in each cell.
            start = random.choice(a)
            end = random.choice(b)

            corridor = []
            for tile in _AStar(start, end):
                if tile not in a and not tile in b:
                    corridor.append(tile)
            rooms.append(corridor)

        # 8. Place staircases in the cell picked in step 2 and the lest cell visited in step 3b.
        stairsUp = random.choice(firstCell.room)
        stairsDown = random.choice(lastCell.room)

        # create tiles
        tiles = {}
        tilesX = cellsX * cellSize
        tilesY = cellsY * cellSize
        for x in range(tilesX):
            for y in range(tilesY):
                tiles[(x, y)] = " "
        for xy in itertools.chain.from_iterable(rooms):
            tiles[xy] = "."

        # every tile adjacent to a floor is a wall
        def getNeighborTiles(xy):
            tx, ty = xy
            for x, y in ((-1, -1), (0, -1), (1, -1),
                        (-1, 0), (1, 0),
                        (-1, 1), (0, 1), (1, 1)):
                try:
                    yield tiles[(tx + x, ty + y)]
                except KeyError:
                    continue

        for xy, tile in tiles.iteritems():
            if not tile == "." and "." in getNeighborTiles(xy):
                tiles[xy] = "#"
        # TODO: floofill on unreachable tiles, and turn them into walls
        tiles[stairsUp] = "<"
        tiles[stairsDown] = ">"

        return tiles

    def char_to_tile(char):
        from barbarian.map import MapTile
        if char == '#':
            return MapTile(blocks=True)
        else:
            return MapTile(blocks=False)

    # MAP_W / 10, (MAP_H - gui crap) / 10, divider
    dividers = (5, 8, 10, 20)       # 16 might crash
    d = random.choice(dividers)
    w, h = 80 / d, 40 / d
    print 'width: %d\nheight: %d\ndivider: %d' % (w, h, d)
    tiles = generate(w, h, d)
    my_map = Map(
        MAP_W, MAP_H,
        [build_entity('base_tile', data_file='mapobjs.json') for _ in range(MAP_W*MAP_H)]
    )

    stairs_x, stairs_y = None, None
    for y in range(MAP_H):
        for x in range(MAP_W):
            char = tiles[(x, y)]
            if char in ('<', '>'):
                my_map[x, y].stairs = char
                stairs_x, stairs_y = x, y
            if char == '#':
                my_map[x, y].blocks = True
                my_map[x, y].blocks_sight = True
            else:
                my_map[x, y].blocks = False
                my_map[x, y].blocks_sight = False

    def post_process_walls():
        # Mark floor tiles outside of any room as walls
        in_room_cells = list(
            my_map.floodfill(stairs_x, stairs_y, lambda c: not c.blocks))
        # print in_room_cells
        """
        for c in in_room_cells:
            c.blocks = True
            c.blocks_sight = True
        """
        for x, y, cell in my_map:
            if cell not in in_room_cells:
                cell.blocks = True
                cell.blocks_sight = True
        # """

    # post_process_walls()

    my_map.init_fov_map()
    return my_map



def make_map_drunken_walk():
    """ Basic drunken walk """
    MAX_TRIES = 5000
    DIRECTIIONS = (
        (0, 1),     # North
        (1, 0),     # East
        (0, -1),    # South
        (-1, 0),    # West
    )

    my_map = Map(
        MAP_W, MAP_H,
        [build_entity('base_tile', data_file='mapobjs.json')
         for _ in range(MAP_W * MAP_H)]
    )

    start_x, start_y = random.randint(20, MAP_W-20), random.randint(20, MAP_H-20)
    x, y = start_x, start_y
    tries = 0
    while tries < MAX_TRIES:
        tries +=1
        my_map[x, y].blocks = False
        my_map[x, y].blocks_sight = False
        dx, dy = random.choice(DIRECTIIONS)
        if (x + dx >= MAP_W or y + dy >= MAP_H or
            x <= 0 or y <= 0):
            continue
        x += dx
        y += dy

    my_map[start_x, start_y].stairs = '<'
    my_map[x, y].stairs = '>'
    my_map.init_fov_map()
    return my_map

