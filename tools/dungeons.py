#! /usr/bin/env python
"""
Quick, hacky visualizer for dungeon generation algorithms.

Try and reuse as much of the game "engine" as possible.

"""
import os, sys
sys.path.append(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
)

from barbarian import libtcodpy as libtcod
from barbarian.io import settings
from barbarian import gamestates
from barbarian.input import common as input
from barbarian import gui
from barbarian.renderers import renderer

import dungeon_builders

# Gamestates overrides...
# I really screwed up on the whole UI/engine separation and this is quite a mess
# to mess around with... Definitely need to rethink this.

class InitState(gamestates.GameState):

    """ Game Initialization. """

    def update(self):
        renderer.init()
        self._replace_with(MainMenuState())


class MainMenuState(gamestates.GameState):

    def __init__(self):
        super(MainMenuState, self).__init__()
        self.map_builders = {
            fname[9:]: getattr(dungeon_builders, fname)
            for fname in dir(dungeon_builders) if fname.startswith('make_map_')
        }
        self.option_list = sorted(self.map_builders.keys())
        from pprint import pprint; pprint(self.map_builders)

        # Lol, worst place ever to be checking sys.argv
        if len(sys.argv) > 1:
            cb = self.map_builders[sys.argv[1]]
            self._replace_with(DungeonState(cb))

    def update(self):

        k = input.collect_keypresses()

        if k is None: return

        if k == '<esc>':
            self._replace_with(gamestates.ShutDownState())
        if k == '<alt>-<return>': #(special case) Alt+Enter: toggle fullscreen
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        #convert the ASCII code to an index; if it corresponds to an option, return it
        if len(k) == 1 and k.isalpha():
            index = ord(k) - ord('a')
            if index >= 0 and index < len(self.option_list):
                callback = self.map_builders[self.option_list[index]]
                self._push(DungeonState(callback))

    def render(self):

        width, height = settings.SCREEN_W, settings.SCREEN_H
        window = libtcod.console_new(width, height)

        y = 5
        letter_index = ord('a')
        for callback_name in self.option_list:
            text = '(' + chr(letter_index) + ') ' + callback_name
            libtcod.console_print_ex(
                window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
            y += 1
            letter_index += 1

        #blit the contents of "window" to the root console
        x = 0
        y = 0
        libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

        libtcod.console_flush()

class DungeonState(gamestates.DungeonState):

    """ Dummy Gameplay State """

    def __init__(self, map_builder_cb):
        from barbarian.dungeon import Dungeon

        super(DungeonState, self).__init__()
        self.map_builder_cb = map_builder_cb

        # Dungeon instanciation buils a first level using a hardcoded building
        # algorithm, which is then discarded by building a new level with the
        # right builder callback. TODO: change Dungeon and/or Level to handle
        # this in a less fugly way.
        self.dungeon = Dungeon()
        self.build_level()

        # Terrible hack to avoid killing cpu with constant redraws.
        # Not sure if the cpukill comes from this tool's other hacks or if
        # it is an actual engin flaw.
        self.redraw = True

    def build_level(self, seed=None):
        from barbarian.dungeon import Level

        import random, sys
        if seed is None:
            seed = random.randint(0, sys.maxint)
        self.seed = seed
        random.seed(seed)
        print 'Random seed: ', seed

        self.dungeon.current_level = Level(map_builder = self.map_builder_cb)
        # self.dungeon.current_level.map.compute_fov(self.player.x, self.player.y)

        for x, y, cell in self.dungeon.current_level.map:
            cell.explored = True

        self.redraw = True

    def process_input(self):

        key  = input.collect_keypresses()
        gui.manager.process_input(key)  # TODO: assign retval to key

        action = input.check_keypress(key, 'std_state')

        if action == 'move_n':
            self.player.move(0, -1, self.dungeon.current_level)
        elif action == 'move_s':
            self.player.move(0, 1, self.dungeon.current_level)
        elif action == 'move_w':
            self.player.move(-1, 0, self.dungeon.current_level)
        elif action == 'move_e':
            self.player.move(1, 0, self.dungeon.current_level)
        elif action == 'move_ne':
            self.player.move(1, -1, self.dungeon.current_level)
        elif action == 'move_se':
            self.player.move(1, 1, self.dungeon.current_level)
        elif action == 'move_sw':
            self.player.move(-1, 1, self.dungeon.current_level)
        elif action == 'move_nw':
            self.player.move(-1, -1, self.dungeon.current_level)

        elif key == '<esc>':
            self._pop()
        elif key == 'n':
            self.build_level()
        elif key == '<shift>-N':
            # DEBUG CRAP
            self.build_level(seed=self.seed)
            m = self.dungeon.current_level.map
            for x, y, c in m:
                if c.stairs == '<':
                    in_room_cells = list(
                        m.floodfill(x, y, lambda c: not c.blocks))
                    # print in_room_cells
                    """
                    for c in in_room_cells:
                        c.blocks = True
                        c.blocks_sight = True
                    """
                    for x, y, cell in m:
                        if cell not in in_room_cells:
                            cell.blocks = True
                            cell.blocks_sight = True
                    break

        return action

    def update(self):
        if self.process_input() is not None:
            self.redraw = True
        self.dungeon.current_level.update()

    def render(self):
        if not self.redraw: return

        renderer.clear()      # TODO: Clear only whats needed...
        renderer.dummy_draw_level(self.dungeon.current_level)
        # renderer.dummy_draw_obj(self.player)
        # Hackish stair drawing - Helpful when the algorithm handle
        # stair placements. Using the regular rendering methods would be better,
        # but they don't handle those yet (and they suck anyway).
        for x, y, c in self.dungeon.current_level.map:
            if c.stairs in ('<', '>'):
                # libtcod.console_set_char_foreground(
                #     0, x, y, render_data.color)
                libtcod.console_set_char(0, x, y, c.stairs)
        # gui.manager.render()

        self.redraw = False


state_manager = gamestates.StateManager(InitState())
while not state_manager.is_done:

    state_manager.update()
