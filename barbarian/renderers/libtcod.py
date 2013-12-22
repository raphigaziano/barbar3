from barbarian import libtcodpy as libtcod

from barbarian.gameio import settings, assets

def init():
    # Dummy console
    # FONT = assets.get_path('fonts', 'terminal.png')
    FONT = assets.get_path('fonts', 'terminal10x10_gs_tc.png')
    # glob.con = libtcod.console_new(CAM_WIDTH, CAM_HEIGHT)

    libtcod.console_set_custom_font(
        FONT, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD
    )
    libtcod.console_init_root(
        settings.SCREEN_W, settings.SCREEN_H, 'Barbarian Quest III', False
    )

    libtcod.sys_set_fps(settings.LIMIT_FPS)

def dummy_main_menu():
    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0,
            settings.SCREEN_W/2, settings.SCREEN_H/2-12,
            libtcod.BKGND_NONE,libtcod.CENTER,
            'BARBARIAN QUEST III')
    libtcod.console_print_ex(0,
            settings.SCREEN_W/2, settings.SCREEN_H/2-8,
            libtcod.BKGND_NONE, libtcod.CENTER,
            'Zangdoz\'s Revenge')
    libtcod.console_print_ex(0,
            settings.SCREEN_W/2, settings.SCREEN_H-2,
            libtcod.BKGND_NONE, libtcod.CENTER,
            'By Zobinet')

    libtcod.console_flush()


def dummy_draw_map(map):
    for x, y, cell in map:
        if cell == 0:
            col = libtcod.light_blue
            ch  = '.'
        elif cell == 1:
            col = libtcod.dark_blue
            ch  = '#'
        # print x, y, col
        libtcod.console_set_char_background(0, x, y, col)
        # libtcod.console_set_char_foreground(0, x, y, col)
        # libtcod.console_set_char(0, x, y, ch)

def dummy_draw_player(x, y):
    libtcod.console_set_char_foreground(0, x, y, libtcod.red)
    libtcod.console_set_char(0, x, y, '@')

def flush():
    libtcod.console_flush()

def clear(con=0):
    libtcod.console_clear(con)
