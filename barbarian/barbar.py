"""
Dummy test file.

Geting back up to speed with libtcod =)

"""
import libtcodpy as libtcod

# Dummy console
FONT = 'barbarian/terminal.png'
# FONT = 'terminal10x10_gs_tc.png'
LIMIT_FPS = 30

SCREEN_W = 80
SCREEN_H = 50

libtcod.console_set_custom_font(FONT)
libtcod.console_init_root(
    SCREEN_W, SCREEN_H, 'Barbarian Quest III', False
)

libtcod.sys_set_fps(LIMIT_FPS)
# glob.con = libtcod.console_new(CAM_WIDTH, CAM_HEIGHT)


while not libtcod.console_is_window_closed():
    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0,
            int(SCREEN_W/2), int(SCREEN_H/2-12),
            libtcod.BKGND_NONE,libtcod.CENTER,
            'BARBARIAN QUEST III')
    libtcod.console_print_ex(0,
            int(SCREEN_W/2), int(SCREEN_H/2-8),
            libtcod.BKGND_NONE, libtcod.CENTER,
            'Zangdoz\'s Revenge')
    libtcod.console_print_ex(0,
            int(SCREEN_W/2), int(SCREEN_H-2),
            libtcod.BKGND_NONE, libtcod.CENTER,
            'By Zobinet')

    libtcod.console_flush()
