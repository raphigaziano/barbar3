# -*- coding: utf8 -*-
"""
barbarian.renderers.libtcod.painter.py
======================================

litdcod rendering functions.
"""
from barbarian import libtcodpy as libtcod

from barbarian.renderers.libtcod.gfxdata import RenderData
from barbarian.io import settings, assets
from barbarian.objects.components import VisibleComponent

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
            libtcod.BKGND_NONE, libtcod.CENTER,
            'BARBARIAN QUEST III')
    libtcod.console_print_ex(0,
            settings.SCREEN_W/2, settings.SCREEN_H/2-8,
            libtcod.BKGND_NONE, libtcod.CENTER,
            'Zangdoz\'s Revenge')
    libtcod.console_print_ex(0,
            settings.SCREEN_W/2, settings.SCREEN_H-2,
            libtcod.BKGND_NONE, libtcod.CENTER,
            'By Zobinet')

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

def dummy_draw_level(level):
    for x, y, cell in level.map:
        if not cell.explored:
            continue
        in_fov = level.map.is_in_fov(x, y)
        if in_fov:
            if cell.blocks_sight:
                col = color_light_wall
            else:
                col = color_light_ground
        else:
            if cell.blocks_sight:
                col = color_dark_wall
            else:
                col = color_dark_ground

        libtcod.console_set_char_background(0, x, y, col)
        # libtcod.console_set_char_foreground(0, x, y, col)
        # libtcod.console_set_char(0, x, y, ch)

    for obj in level.objects.filter_by_components(VisibleComponent):
        if level.map.is_obj_in_fov(obj):
            dummy_draw_obj(obj)

def dummy_draw_obj(obj):
    from barbarian.io.data import read_data_file
    gfxdata = read_data_file(
        'graphics/libtcod/entities_props.json'
    )[obj.entity_name]
    render_data = RenderData(color=gfxdata['color'])
    libtcod.console_set_char_foreground(0, obj.x, obj.y, render_data.color)
    # /!\ Libtcod needs byte strings /!\
    libtcod.console_set_char(0, obj.x, obj.y, str(obj.char))

tcod_consoles = {}
def dummy_draw_console(con, x, y, blit_on=0):
    """
    Blits the widget to the console passed as parameter (defaults to
    the root console), with its top-left corner at the specified
    x:y position.
    This is the bare minimum any widget will have to do to draw
    itself.
    """
    # if self.framed:
    #     # draw an old school looking frame around the window \o/
    #     libtcod.console_set_foreground_color(con, self.frame_color)
    #     libtcod.console_print_frame(self.con, 0, 0, self.w, self.h,
    #                                 False, libtcod.BKGND_NONE, self.title)
    # blit any children on the widget's console
    # for child in con.children:
    #     child.display()
    # Blit self
    # !TEMPO!
    if id(con) not in tcod_consoles:
        new_console = libtcod.console_new(con.w, con.h)
        # libtcod.console_set_default_foreground(new_console, libtcod.white)
        # libtcod.console_set_default_background(new_console, libtcod.blue)
        libtcod.console_clear(new_console)
        tcod_consoles[id(con)] = new_console

    tcod_cons = tcod_consoles[id(con)]

    # if con.dirty:
    #     libtcod.console_clear(tcod_cons)
    #     con.dirty = False

    libtcod.console_print_frame(tcod_cons, 0, 0, con.w, con.h,
                                # False, # BACKGROUND_FLAG, title
                                )
    # /TEMPO!

    # for i, msg in enumerate(con.msgs[-(8+offset):-(offset)]):
    offset = 1 # TEMPO
    for i, msg in enumerate(con.last_msgs[-(con.h-2):]):
        # HACKKKKKKKKKKKKKKKK
        rdata = RenderData(color=msg.col)
        libtcod.console_set_default_foreground(tcod_cons, rdata.color)
        libtcod.console_print_rect(
            tcod_cons, 1, offset, con.w-2, con.h-2, msg.txt
        )
        offset += libtcod.console_get_height_rect(
            tcod_cons, 1, offset, con.w-2, con.h-2, msg.txt
        )

    libtcod.console_blit(tcod_cons, 0, 0, con.w, con.h, blit_on, x, y,)
                        # self.forealpha, self.backalpha)
    # libtcod.console_flush()

def flush():
    libtcod.console_flush()

def clear(con=0):
    libtcod.console_clear(con)
