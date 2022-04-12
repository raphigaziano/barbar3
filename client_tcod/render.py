"""
TCOD initialization & Rendering routines.

"""
import os
import textwrap

from . import constants as C

import tcod

# TILESHEET_NAME = 'dejavu10x10_gs_tc.png'
# TILESHEET_CELL_W, TILESHEET_CELL_H = 32, 8
# TILESHEET_CHARMAP = tcod.tileset.CHARMAP_TCOD
# TILESHEET_NAME = 'Markvii.png'
# TILESHEET_CELL_W, TILESHEET_CELL_H = 16, 16
# TILESHEET_CHARMAP = tcod.tileset.CHARMAP_CP437
# TILESHEET_NAME = 'Cheepicus_14x14.png'
# TILESHEET_CELL_W, TILESHEET_CELL_H = 16, 16
# TILESHEET_CHARMAP = tcod.tileset.CHARMAP_CP437
TILESHEET_NAME = 'terminal10x10_gs_tc.png'
TILESHEET_CELL_W, TILESHEET_CELL_H = 32, 8
TILESHEET_CHARMAP = tcod.tileset.CHARMAP_TCOD

TileGlyphs = {
    C.TileType.FLOOR: '.',
    C.TileType.WALL: '#',
}

# fg
TileColors = {
    C.TileType.FLOOR: tcod.Color(0, 127, 0),
    C.TileType.WALL: tcod.Color(0, 255, 0),
}

HUNGER_STATE_COLORS = {
    'full': tcod.light_green,
    'very hungry': tcod.yellow,
    'starving': tcod.orange,
}

GFX_DATA = {
    'player': {'glyph': '@', 'fg_color': tcod.yellow},
    'orc': {'glyph': 'O', 'fg_color': tcod.green},
    'orc_boss': {'glyph': 'O', 'fg_color': tcod.dark_green},
    'kobold': {'glyph': 'k', 'fg_color': tcod.red},
    'trap': {'fg_color': tcod.red},
    'trap_depleted': {'fg_color': tcod.grey},
    'open_door': {
        'glyph': '+', 'fg_color': TileColors[C.TileType.FLOOR]},
    'closed_door': {'fg_color': tcod.yellow},
    'food': {'fg_color': tcod.green},
}

TRANS_COLOR = tcod.Color(255, 0, 255)

FLOOR_BG = None
FLOOR_BG_OOF = None

BLOOD_COLOR = tcod.Color(63, 0, 0)

PROGRESS_BAR_LABEL_COLOR = tcod.white

HEALTH_BAR_BG_COLOR = tcod.black
HEALTH_BAR_FG_COLOR = tcod.dark_red

HUNGER_BAR_BG_COLOR = tcod.black
HUNGER_BAR_FG_COLOR = tcod.darker_green

TOOLTIP_FG = tcod.yellow
TOOLTIP_BG = tcod.black

LOG_FG = tcod.yellow
LOG_BG = tcod.black
LOG_FRAME_FG = tcod.white
LOG_FRAME_BG = tcod.black

STATS_FG = tcod.yellow
STATS_BG = tcod.black
STATS_FRAME_FG = tcod.white
STATS_FRAME_BG = tcod.black

MODAL_FRAME_FG = tcod.white
MODAL_FRAME_BG = tcod.black
MODAL_FG = tcod.yellow
MODAL_BG = tcod.black

MENU_FRAME_FG = tcod.white
MENU_FRAME_BG = tcod.black
MENU_BG = tcod.black
MENU_FG = tcod.white
MENU_ITEM_FG = tcod.white
MENU_ITEM_BG = tcod.black
MENU_CURSOR_FG = tcod.yellow
MENU_CURSOR_BG = tcod.black

GAMEOVER_FG = tcod.red
GAMEOVER_BG = tcod.black

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
        tilesheet_path = os.path.join(
            C.ASSETS_PATH, 'fonts', TILESHEET_NAME)
        ts = tcod.tileset.load_tilesheet(
            tilesheet_path, 
            TILESHEET_CELL_W, TILESHEET_CELL_H, TILESHEET_CHARMAP)

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
                bg_color = BLOOD_COLOR if [x,y] in bloodstains else FLOOR_BG
                if not show_whole_map and not visible[cell_idx]:
                    fg_color = tcod.grey
                    bg_color = FLOOR_BG_OOF
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
        if e['type'] == 'trap':
            if e['consumable']['charges'] <= 0:
                return GFX_DATA['trap_depleted']

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
                    if (e['type'] not in C.IGNORE_FOV_ENTITY_TYPES or
                        not explored[vis_idx]
                    ):
                        continue
                self.render_entity(layer_console, e)

            layer_console.blit(self.map_console, bg_alpha=0.0)

        map_w = gamestate.map['width']
        visible = gamestate.visible_cells
        explored = gamestate.explored_cells

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
                        left_x, y, width, 1, s, TOOLTIP_FG, TOOLTIP_BG)
                    y += 1
                self.hud_console.print(
                    arrow_pos_x, arrow_pos_y, '->', TOOLTIP_FG, TOOLTIP_BG)
            else:
                (arrow_pos_x, arrow_pos_y) = mx + 1, my
                left_x = mx + 3
                y = my
                for s in tooltip:
                    self.hud_console.print_box(
                        left_x + 1, y, width, 1, s, TOOLTIP_FG, TOOLTIP_BG)
                    y += 1
                self.hud_console.print(
                    arrow_pos_x, arrow_pos_y, '<-', TOOLTIP_FG, TOOLTIP_BG)

    _path_colors = [tcod.yellow, tcod.orange, tcod.red, tcod.purple, tcod.blue]
    _zone_colors = []

    def render_debug_overlays(self, gamestate):
        if C.SHOW_PATH_INFO:
            for idx, cval in enumerate(gamestate.map['pathmap']):
                x, y = idx_to_c(idx, gamestate.map['width'])
                if cval == 0:
                    color = tcod.red
                else:
                    col_idx = cval // 10
                    color = (
                        self._path_colors[col_idx] if col_idx < len(self._path_colors)
                        else tcod.white)
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
                    self.hud_console.print(x, y, str(i), color, bg=tcod.black)

    def render_hud(self, gamestate):
        self.hud_console.clear(bg=TRANS_COLOR)

        mouse_state = tcod.event.get_mouse_state()
        self.context.convert_event(mouse_state)

        self.render_debug_overlays(gamestate)
        self.render_tooltips(gamestate, mouse_state)

        if C.SHOW_DEBUG_INFO:
            # self.hud_console.print(
            #   0, 0, f'mean fps: {gamestate.clock.mean_fps:.2f}', tcod.yellow)
            self.hud_console.print(
                0, 0, f'median fps: {gamestate.clock.median_fps:.2f}',
                fg=tcod.yellow, bg=tcod.black)
            self.hud_console.print(
                0, 1, f'mouse pos: {mouse_state.tile}', fg=tcod.yellow, bg=tcod.black)

        self.hud_console.blit(self.map_console, key_color=TRANS_COLOR)

    def _render_stat_bar(
        self, console, x, y, val, max_val, label,
        bar_length, label_fg, bar_fg, bar_bg
    ):
        bar_total_length = bar_length
        bar_length = int(val / max_val * bar_total_length)

        console.draw_rect(x, y, bar_total_length, 1, 0, bg=bar_bg)
        console.draw_rect(x, y, bar_length, 1, 0, bg=bar_fg)
        console.print_box(
            x, y, bar_total_length, 1, label, fg=label_fg, alignment=tcod.CENTER)

    def render_stats(self, gamestate):
        self.stats_console.clear(fg=STATS_FG, bg=STATS_BG)

        self.stats_console.draw_frame(
            0, 0, C.STATS_CONSOLE_W, C.STATS_CONSOLE_H,
            fg=STATS_FRAME_FG, bg=STATS_FRAME_BG)
        self.stats_console.print_box(
            0, 0, C.STATS_CONSOLE_W, 1, " Stats ",
            fg=STATS_FRAME_FG, bg=STATS_FRAME_BG, alignment=tcod.CENTER)

        cd, md = gamestate.current_depth, gamestate.max_depth
        self.stats_console.print(
            2, 1, f'Current depth: {cd}/{md}', fg=STATS_FG, bg=STATS_BG)

        hp = gamestate.player['health']['hp']
        max_hp = gamestate.player['health']['max_hp']

        health_bar_label = f'HP: {hp}/{max_hp}'
        self._render_stat_bar(
            self.stats_console, 2, 3, hp, max_hp, health_bar_label,
            C.STATS_CONSOLE_W - 4,
            PROGRESS_BAR_LABEL_COLOR, HEALTH_BAR_FG_COLOR, HEALTH_BAR_BG_COLOR)

        hunger_clock = gamestate.player['hunger_clock']
        hunger, max_hunger = (
            hunger_clock['satiation'], hunger_clock['max_satiation'])
        hunger_state = hunger_clock['state']
        hunger_label = f'Hunger: {hunger_state}'
        hunger_label_color = HUNGER_STATE_COLORS.get(
            hunger_state, PROGRESS_BAR_LABEL_COLOR)
        self._render_stat_bar(
            self.stats_console, 2, 4, hunger, max_hunger, hunger_label,
            C.STATS_CONSOLE_W - 4, hunger_label_color,
            HUNGER_BAR_FG_COLOR, HUNGER_BAR_BG_COLOR)

        str_ = gamestate.player['stats']['strength']
        self.stats_console.print(
            2, 6, f'Strength: {str_}', fg=STATS_FG, bg=STATS_BG)

        self.stats_console.blit(self.root_console, C.STATS_CONSOLE_X, C.STATS_CONSOLE_Y)

    def render_log(self, gamelog):
        self.log_console.clear(fg=LOG_FG, bg=LOG_BG)

        self.log_console.draw_frame(
            0, 0, C.LOG_CONSOLE_W, C.LOG_CONSOLE_H,
            fg=LOG_FRAME_FG, bg=LOG_FRAME_BG)
        self.log_console.print_box(
            0, 0, C.LOG_CONSOLE_W, 1, " Message Log ",
            fg=LOG_FRAME_FG, bg=LOG_FRAME_BG, alignment=tcod.CENTER)

        log_border = 2
        log_w, log_h = C.LOG_CONSOLE_W - log_border, C.LOG_CONSOLE_H - log_border

        msgs = self._wrap_lines(
            [f'[{t}] - {m}' for (t, m) in gamelog], log_w, log_h)

        offsety = 1
        for i, msg in enumerate(msgs):
            y = i
            # print_box or print_rect ?
            offsety += self.log_console.print_box(
                1, y+offsety, log_w, C.LOG_CONSOLE_H-offsety, msg,
                fg=LOG_FG, bg=LOG_BG
            ) - 1

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

    def render_modal(self, modal_title, modal_text, offset=9):

        self.hud_console.clear(bg=TRANS_COLOR)

        lines = textwrap.dedent(modal_text).splitlines()
        if len(lines) > (C.MAX_MODAL_HEIGHT - 2):
            start_idx = offset
            end_idx = min(C.MAX_MODAL_HEIGHT + offset, len(lines))
        else:
            start_idx, end_idx = 0, len(lines)
        wrapped = self._wrap_lines(
            lines[start_idx:end_idx], C.MAX_MODAL_WIDTH-2, C.MAX_MODAL_HEIGHT-2)

        modal_width, modal_height = (
            min(C.MAX_MODAL_WIDTH, max(map(len, lines))) + 2,
            min(C.MAX_MODAL_HEIGHT, len(wrapped) + 2)
        )
        modal_x, modal_y = (
            (C.SCREEN_W // 2) - (modal_width // 2),
            (C.MAP_VIEWPORT_H // 2) - (modal_height // 2)
        )

        self.hud_console.draw_frame(
            modal_x-2, modal_y-2, modal_width + 4, modal_height + 2,
            title=f' {modal_title} ' if modal_title else None,
            fg=MODAL_FRAME_FG, bg=MODAL_FRAME_BG)
        self.hud_console.print_box(
            modal_x, modal_y, modal_width, modal_height, '\n'.join(wrapped),
            MODAL_FG, MODAL_BG)

        self.hud_console.blit(self.root_console, key_color=TRANS_COLOR)
        self.context.present(self.root_console)

    def render_menu(self, menu_mode):

        self.hud_console.clear(bg=TRANS_COLOR)

        menu_opts = menu_mode.menu_options
        cursor_idx = menu_mode.cursor_idx

        if menu_opts:
            menu_width = max(
                len(item_name) + 5 for _, item_name in menu_opts) + 6
            menu_height = len(menu_opts) + 5
        else:
            menu_width, menu_height = 30, 8
        menu_x, menu_y = (C.SCREEN_W // 2) - (menu_width // 2), 15

        self.hud_console.draw_frame(
            menu_x, menu_y, menu_width, menu_height,
            fg=MENU_FRAME_FG, bg=MENU_FRAME_BG)
        self.hud_console.print_box(
            menu_x, menu_y, menu_width, 1, f' {menu_mode.title} ',
            MENU_FRAME_FG, MENU_FRAME_BG, alignment=tcod.CENTER)

        opts_offset_x = menu_x + 2
        opts_offset_y = menu_y + 3

        for i, (_, item_name) in enumerate(menu_opts):
            item_str = f'({chr(65 + i)}) - {item_name}'
            fg = MENU_CURSOR_FG if (i == cursor_idx) else MENU_ITEM_FG
            bg = MENU_CURSOR_BG if (i == cursor_idx) else MENU_ITEM_BG
            self.hud_console.print(
                opts_offset_x, opts_offset_y + i, item_str, fg=fg, bg=bg)

        self.hud_console.blit(self.root_console, key_color=TRANS_COLOR)
        self.context.present(self.root_console)

    def render_gameover_screen(self, gamestate):

        self.hud_console.clear(bg=GAMEOVER_BG)

        msg = 'You are dead!'
        msg_x, msg_y = (C.SCREEN_W // 2) - (len(msg) // 2), 20
        self.hud_console.print(msg_x, msg_y, msg, GAMEOVER_FG)

        msg = 'Press n to start a new run, or escape to quit.'
        msg_x, msg_y = (C.SCREEN_W // 2) - (len(msg) // 2), 25
        self.hud_console.print(msg_x, msg_y, msg, GAMEOVER_FG)

        self.hud_console.blit(self.root_console, bg_alpha=0.03)
        self.context.present(self.root_console)

    def flash_color(self, r, g, b):
        c = tcod.Color(r, g, b)
        self.hud_console.clear(bg=c)
        self.hud_console.blit(self.root_console, bg_alpha=0.3)
        self.context.present(self.root_console)

    def _wrap_lines(self, lines, max_width, max_height):

        wrapped_lines = []
        total_lines = 0
        for s in reversed(lines):
            if not s:
                wrapped = [s]
            else:
                for l in reversed(s.splitlines()):
                    wrapped = textwrap.wrap(l, max_width)
            for l in reversed(wrapped):
                wrapped_lines.insert(0, l)
                total_lines += 1
                if total_lines >= max_height:
                    return wrapped_lines
        return wrapped_lines
