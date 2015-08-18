import random
from barbarian.map import Map
from barbarian.utils import rng, geometry

from barbarian.io.settings import MAP_W, MAP_H
from barbarian.objects.factories import build_entity


def make_map_basic_bsp():
    """
    Basic BSP, inspired by http://eskerda.com/bsp-dungeon-generation/

    """

    class Tree:

        def __init__(self, leaf):
            self.leaf = leaf
            self.l_child = None
            self.r_child = None

        @property
        def leaves(self):
            if not (self.l_child and self.r_child):
                return [self.leaf]
            else:
                return self.l_child.leaves + self.r_child.leaves

        def get_level(self, level, queue=None):     # TODO: prolly rename

            if queue is None:
                queue = []
            if level == 1 :
                queue.append(self)
            else:
                if self.l_child:
                    self.l_child.get_level(level-1, queue)
                if self.r_child:
                    self.r_child.get_level(level-1, queue)

            return queue

        def fill_grid(self, map_):
            # NOPE!
            # At least not for dummy draw: parent leaves will overwrite their children
            self.leaf.fill_grid(map_)
            if self.l_child:
                self.l_child.fill_grid(map_)
            if self.r_child:
                self.r_child.fill_grid(map_)


    class Container:
        # Meh. Just reuse geometry Rect.
        def __init__(self, x, y, w, h):
            self.x = x
            self.y = y
            self.w = w
            self.h = h

        def __repr__(self):
            return ('({0.x},{0.y},{0.w},{0.h})'.format(self))

        @property
        def center(self):
            return self.x + (self.w / 2), self.y + (self.h / 2)

        def fill_grid(self, map_):
            room_offset = 1
            for x in range(self.x+room_offset, self.x+self.w):
                for y in range(self.y+room_offset, self.y+self.h):
                    my_map[x, y].blocks = False
                    my_map[x, y].blocks_sight = False

    def split_container(container, iter, discard_by_ratio, w_ratio, h_ratio):
        # - print container
        root = Tree(container)
        if iter != 0:
            sr = None
            while sr is None:
                sr = random_split(container, discard_by_ratio, w_ratio, h_ratio)
            root.l_child = split_container(sr[0], iter-1, discard_by_ratio, w_ratio, h_ratio)
            root.r_child = split_container(sr[1], iter-1, discard_by_ratio, w_ratio, h_ratio)
        return root

    def random_split(container, discard_by_ratio, w_ratio, h_ratio):
        r1, r2 = None, None
        if random.randint(0, 1) == 0:
            # Vertical
            r1 = Container(
                container.x, container.y,                       # r1.x, r1.y
                random.randint(1, container.w), container.h     # r1.w, r1.h
            )
            r2 = Container(
                container.x + r1.w, container.y,                # r2.x, r2.y
                container.w - r1.w, container.h                 # r2.w, r2.h
            )
            if discard_by_ratio:
                r1_w_ratio = r1.w / float(r1.h)
                r2_w_ratio = r2.w / float(r2.h)
                if r1_w_ratio < w_ratio or r2_w_ratio < w_ratio:
                    return random_split(container, discard_by_ratio, w_ratio, h_ratio)
        else:
            # Horizontal
            r1 = Container(
                container.x, container.y,                       # r1.x, r1.y
                container.w, random.randint(1, container.h)     # r1.w, r1.h
            )
            r2 = Container(
                container.x, container.y + r1.h,                # r2.x, r2.y
                container.w, container.h - r1.h                 # r2.w, r2.h
            )
            if discard_by_ratio:
                r1_h_ratio = r1.h / float(r1.w)
                r2_h_ratio = r2.h / float(r2.w)
                if r1_h_ratio < h_ratio or r2_h_ratio < h_ratio:
                    return random_split(container, discard_by_ratio, w_ratio, h_ratio)
        return r1, r2

    my_map = Map(
        MAP_W, MAP_H,
        [build_entity('base_tile', data_file='mapobjs.json')
         for _ in range(MAP_W * MAP_H)]
    )

    DISCARD_BY_RATIO = True
    W_RATIO          = 0.35
    H_RATIO          = 0.35
    N_SPLITS = 4

    main_container = Container(0, 0, MAP_W, MAP_H)
    container_tree = split_container(main_container, N_SPLITS, DISCARD_BY_RATIO, W_RATIO, H_RATIO)

    for c in container_tree.get_level(N_SPLITS):
        c.fill_grid(my_map)

    my_map.init_fov_map()
    return my_map
