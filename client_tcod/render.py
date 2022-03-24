"""
TCOD initialization & Rendering routines.

"""
import os

from . import constants as C

import tcod


TileGlyphs = {
    C.TileType.FLOOR: '.',
    C.TileType.WALL: '#',
}

TileColors = {
    C.TileType.FLOOR: tcod.Color(0, 127, 0),
    C.TileType.WALL: tcod.Color(0, 255, 0),
}

GFX_DATA = {
    'player': {'glyph': '@', 'fg_color': tcod.yellow},
    'orc': {'glyph': 'O', 'fg_color': tcod.green},
    'kobold': {'glyph': 'k', 'fg_color': tcod.red},
    'trap': {'fg_color': tcod.red},
    'open_door': {
        'glyph': '+', 'fg_color': TileColors[C.TileType.FLOOR]},
    'closed_door': {'fg_color': tcod.yellow},
}

BLOOD_COLOR = tcod.Color(63, 0, 0)
TOOLTIP_FG = tcod.yellow

CP437_GLYPHS = {
    0:  9,      # Pillar because we can't see neighbors
    1:  186,    # Wall only to the north
    2:  186,    # Wall only to the south
    3:  186,    # Wall to the north and south
    4:  205,    # Wall only to the west
    5:  188,    # Wall to the north and west
    6:  187,    # Wall to the south and west
    7:  185,    # Wall to the north, south and west
    8:  205,    # Wall only to the east
    9:  200,    # Wall to the north and east
    10:  201,   # Wall to the south and east
    11:  204,   # Wall to the north, south and east
    12:  205,   # Wall to the east and west
    13:  202,   # Wall to the east, west, and south
    14:  203,   # Wall to the east, west, and north
    15:  206,   # ╬ Wall on all sides
}

CP437_FALLBACK_GLYPH = 35


def idx_to_c(idx, width):
    """ Convert array index to cartesian coordinates. """
    return idx % width, idx // width

def c_to_idx(x, y, width):
    """ Convert cartesian coordinates to internal array index. """
    return x + (y * width)


class TcodRenderer:
    """ Handle all rendering, deferring to the tcod API """

    def __init__(self):
        self.context = None

    def init_tcod(self):
        # tilesheet_name = 'dejavu10x10_gs_tc.png'
        # tilesheet_cell_w, tilesheet_cell_h = 32, 8
        # tilesheet_name = 'Markvii.png'
        # tilesheet_cell_w, tilesheet_cell_h = 16, 16
        # tilesheet_name =' Cheepicus_14x14.png'
        # tilesheet_cell_w, tilesheet_cell_h = 16, 16
        tilesheet_name = 'terminal10x10_gs_tc.png'
        tilesheet_cell_w, tilesheet_cell_h = 32, 8
        tilesheet_path = os.path.join(C.ASSETS_PATH, 'fonts', tilesheet_name)
        ts = tcod.tileset.load_tilesheet(
            tilesheet_path, tilesheet_cell_w, tilesheet_cell_h,
            tcod.tileset.CHARMAP_TCOD)

        self.context = tcod.context.new(
            columns=C.SCREEN_W, rows=C.SCREEN_H,
            tileset=ts,
            title="BarbarianQuest",
            # context.new peeks into sys.argv by default, which eats
            # some of our own arguments. Pass in an empty list to prevent
            # this.
            argv=[],
        )
        return self.context

    def shutdown_tcod(self):
        self.context.close()

    def init_consoles(self):

        self.root_console = self.context.new_console(magnification=1.0)

        self.map_console = tcod.Console(C.MAP_VIEWPORT_W, C.MAP_VIEWPORT_H)

        self.props_console = tcod.Console(C.MAP_VIEWPORT_W, C.MAP_VIEWPORT_W)
        self.items_console = tcod.Console(C.MAP_VIEWPORT_W, C.MAP_VIEWPORT_W)
        self.actors_console = tcod.Console(C.MAP_VIEWPORT_W, C.MAP_VIEWPORT_W)

        self.hud_console = tcod.Console(C.MAP_VIEWPORT_W, C.MAP_VIEWPORT_H)

        self.stats_console = tcod.Console(C.STATS_CONSOLE_W, C.STATS_CONSOLE_H)
        self.log_console = tcod.Console(C.LOG_CONSOLE_W, C.LOG_CONSOLE_H)

    def render_map(self, m, explored, visible, bloodstains, show_whole_map=False):
        self.map_console.clear()

        cells = m['cells']
        bitmask_grid = m.get('bitmask_grid', None)

        for cell_idx, c in enumerate(cells):
            x, y = idx_to_c(cell_idx, m['width'])
            if not show_whole_map and not explored[cell_idx]:
                continue
            c = C.TileType(c)
            bitmask = bitmask_grid[cell_idx] if bitmask_grid else None
            # if bitmask != 35:
            if c == C.TileType.WALL:
                # if bitmask in (15,): continue
                ch = tcod.tileset.CHARMAP_CP437[
                    CP437_GLYPHS.get(bitmask, CP437_FALLBACK_GLYPH)]
                self.map_console.put_char(x, y, ch)
            else:
                fg_color = TileColors.get(c)
                bg_color = BLOOD_COLOR if [x,y] in bloodstains else None
                if not show_whole_map and not visible[cell_idx]:
                    fg_color = tcod.grey
                    bg_color = None
                ch = TileGlyphs.get(c, ' ')
                self.map_console.print(x, y, ch, fg_color, bg_color)

    def render_map_debug(self, cells):
        self.render_map(cells, [], [], [], show_whole_map=True)

        self.map_console.blit(self.root_console)
        self.context.present(self.root_console)

    def _get_gfx_data(self, e):

        if e['type'] == 'door':
            if e['openable']['open']:
                return GFX_DATA['open_door']
            else:
                return GFX_DATA['closed_door']

        return GFX_DATA.get(e['type'], {})

    def render_entity(self, layer_console, e):
        _gfxdata = self._get_gfx_data(e)
        gfxd = {
            'glyph': _gfxdata.get('glyph', e['visible']['glyph']),
            'fg_c': _gfxdata.get('fg_color', tcod.white),
            'bg_c': _gfxdata.get('bg_color')
        }
        x, y = e['pos']
        layer_console.print(x, y, gfxd['glyph'], gfxd['fg_c'], gfxd['bg_c'])

    def render_entities(self, gamestate):

        def _render_entity_list(layer_console, entities):
            layer_console.clear()

            for e in entities:
                ex, ey = e['pos']
                vis_idx = c_to_idx(ex, ey, map_w)
                if not C.IGNORE_FOV and not visible[vis_idx]:
                    continue
                self.render_entity(layer_console, e)

            layer_console.blit(self.map_console, bg_alpha=0.0)

        map_w = gamestate.map['width']
        visible = gamestate.visible_cells

        _render_entity_list(self.props_console, gamestate.props)
        _render_entity_list(self.items_console, gamestate.items)
        _render_entity_list(self.actors_console, gamestate.actors)

    def render_viewport(self, gamestate, bloodstains):
        self.render_map(
            gamestate.map,
            gamestate.explored_cells,
            gamestate.visible_cells,
            bloodstains,
            show_whole_map=C.SHOW_UNEXPLORED_CELLS)


        self.render_entities(gamestate)
        self.render_hud(gamestate)

        self.map_console.blit(self.root_console)

    def render_tooltips(self, gamestate, mouse_state):

        map_w = gamestate.map['width']
        mx, my = mouse_state.tile.x, mouse_state.tile.y

        if mx < 0 or mx >= C.MAP_VIEWPORT_W or my < 0 or my >= C.MAP_VIEWPORT_H:
            return
        if not C.IGNORE_FOV and not gamestate.visible_cells[c_to_idx(mx, my, map_w)]:
            return

        tooltip = []

        for a in gamestate.actors:
            if a['pos'] == [mx, my]:
                tooltip.append(f"{a['name']} ({a['id']})")
        for a in gamestate.items:
            if a['pos'] == [mx, my]:
                tooltip.append(f"{a['name']} ({a['id']})")
        for a in gamestate.props:
            if a['pos'] == [mx, my]:
                tooltip.append(f"{a['name']} ({a['id']})")

        if tooltip:
            width = 0
            for s in tooltip:
                if width < len(s): width = len(s)
            width += 3

            if mx > C.SCREEN_W // 2:
                (arrow_pos_x, arrow_pos_y) = mx - 2, my
                left_x = mx - width
                y = my
                for s in tooltip:
                    self.hud_console.print_box(
                        left_x, y, width, 1, s, TOOLTIP_FG)
                    y += 1
                self.hud_console.print(
                    arrow_pos_x, arrow_pos_y, '->', TOOLTIP_FG)
            else:
                (arrow_pos_x, arrow_pos_y) = mx + 1, my
                left_x = mx + 3
                y = my
                for s in tooltip:
                    self.hud_console.print_box(
                        left_x + 1, y, width, 1, s, TOOLTIP_FG)
                    y += 1
                self.hud_console.print(
                    arrow_pos_x, arrow_pos_y, '<-', TOOLTIP_FG)

    _zone_colors = []
    def render_debug_overlays(self, gamestate):
        if C.SHOW_PATH_INFO:
            for idx, cval in enumerate(gamestate.map['pathmap']):
                x, y = idx_to_c(idx, gamestate.map['width'])
                cols = [tcod.yellow, tcod.orange, tcod.red, tcod.purple, tcod.blue]
                col_idx = cval // 10
                color = cols[col_idx] if col_idx < len(cols) else tcod.white
                char = str(cval)[-1]
                self.hud_console.print(x, y, char, color, bg=tcod.black)

        if C.SHOW_SPAWN_ZONES:
            import random
            for i, zone in enumerate(gamestate.spawn_zones):
                if i >= len(self._zone_colors):
                    color = tcod.Color(
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255))
                    self._zone_colors.append(color)
                else:
                    color = self._zone_colors[i]
                for x, y in zone:
                    self.hud_console.print(x, y, str(i), color)

    def render_hud(self, gamestate):
        self.hud_console.clear()

        self.render_debug_overlays(gamestate)

        mouse_state = tcod.event.get_mouse_state()
        self.context.convert_event(mouse_state)
        self.render_tooltips(gamestate, mouse_state)

        # self.hud_console.print(
        #   0, 0, f'mean fps: {gamestate.clock.mean_fps:.2f}', tcod.yellow)
        self.hud_console.print(
            0, 0, f'median fps: {gamestate.clock.median_fps:.2f}', tcod.yellow)

        self.hud_console.blit(self.map_console, bg_alpha=0.0)

    def render_stats(self, gamestate):
        self.stats_console.clear()

        self.stats_console.draw_frame(0, 0, C.STATS_CONSOLE_W, C.STATS_CONSOLE_H)
        self.stats_console.print_box(
            0, 0, C.STATS_CONSOLE_W, 1, " Stats ", fg=tcod.black, bg=tcod.white, alignment=tcod.CENTER)

        cd, md = gamestate.current_depth, gamestate.max_depth
        self.stats_console.print(1, 1, f'Current depth: {cd}/{md}')

        hp = gamestate.player['health']['hp']
        str_ = gamestate.player['stats']['strength']
        self.stats_console.print(1, 3, f'HP: {hp}')
        self.stats_console.print(1, 4, f'Strength: {str_}')

        self.stats_console.blit(self.root_console, C.STATS_CONSOLE_X, C.STATS_CONSOLE_Y)

    def render_log(self, gamelog):
        self.log_console.clear()

        self.log_console.draw_frame(0, 0, C.LOG_CONSOLE_W, C.LOG_CONSOLE_H)
        self.log_console.print_box(
            0, 0, C.LOG_CONSOLE_W, 1, " Message Log ", fg=tcod.black, bg=tcod.white, alignment=tcod.CENTER)

        log_border = 2
        log_w, log_h = C.LOG_CONSOLE_W - log_border, C.LOG_CONSOLE_H - log_border

        # Handling multiline messages.
        # This works, except that when a multiline string reached the top,
        # it messes up the indexing for following messages.
        # For exemple, is m is 4 lines, then the log won't budge until 4
        # new messages appear, and those will then all be displayed at
        # once.
        # Not sure how to fix it, but since we'll probably need to change
        # this to handle log coloring at some point, *and* we're not even
        # sure we'll have to handle multiline logging anyway, I'd rather
        # just leave it out for now.
        #
        # start_msg_index = len(gamelog)
        # total_lines = 0
        # for (t, m) in reversed(gamelog):
        #     s = f'[{t}] - {m}'
        #     numlines = self.log_console.get_height_rect(0, 0, log_w, log_h, s)
        #     total_lines += numlines
        #     start_msg_index -= abs(min(1, abs(total_lines-log_h)))
        #     if total_lines > log_h:
        #         break
        # msgs = gamelog[start_msg_index:]
        # ...

        msgs = gamelog[-log_h:]
        offsety = 1
        for i, (t, m) in enumerate(msgs):
            msg = f'[{t}] - {m}'
            y = i
            # print_box or print_rect ?
            offsety += self.log_console.print_box(
                1, y+offsety, log_w, C.LOG_CONSOLE_H-offsety, msg) - 1

        self.log_console.blit(self.root_console, C.LOG_CONSOLE_X, C.LOG_CONSOLE_Y)

    def render_ui(self, gamestate, gamelog):
        self.render_stats(gamestate)
        self.render_log(gamelog)

    def render_all(self, gamestate, gamelog, bloodstains):
        """ Main rendering method """

        self.root_console.clear()

        self.render_viewport(gamestate, bloodstains)
        self.render_ui(gamestate, gamelog)

        self.context.present(self.root_console)

    def render_gameover_screen(self, gamestate):
        self.render_hud(gamestate)

        msg = 'You are dead!'
        msg_x, msg_y = (C.SCREEN_W // 2) - (len(msg) // 2), 20
        self.hud_console.print(msg_x, msg_y, msg, tcod.red)

        msg = 'Press n to start a new run, or escape to quit.'
        msg_x, msg_y = (C.SCREEN_W // 2) - (len(msg) // 2), 25
        self.hud_console.print(msg_x, msg_y, msg, tcod.red)

        self.hud_console.blit(self.root_console, bg_alpha=0.03)
        self.context.present(self.root_console)
