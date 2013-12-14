"""
barbarian.barbar.py
===================

Game entry point.

"""
# pylint: disable=E1101
import libtcodpy as libtcod

from utils import settings, assets

# Dummy console
FONT = assets.get_path('terminal.png')
# FONT = 'barbarian/terminal10x10_gs_tc.png'

libtcod.console_set_custom_font(FONT)
libtcod.console_init_root(
    settings.SCREEN_W, settings.SCREEN_H, 'Barbarian Quest III', False
)

libtcod.sys_set_fps(settings.LIMIT_FPS)
# glob.con = libtcod.console_new(CAM_WIDTH, CAM_HEIGHT)


while not libtcod.console_is_window_closed():
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
