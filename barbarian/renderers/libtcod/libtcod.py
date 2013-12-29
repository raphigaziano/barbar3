from barbarian import libtcodpy as libtcod

from barbarian.renderers.libtcod import colors
from barbarian.io import settings, assets

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


def dummy_draw_level(level):
    for x, y, cell in level.map:
        if cell.blocks_sight:
            col = libtcod.dark_blue
            ch  = '#'
        else:
            col = libtcod.light_blue
            ch  = '.'
        # print x, y, col
        libtcod.console_set_char_background(0, x, y, col)
        # libtcod.console_set_char_foreground(0, x, y, col)
        # libtcod.console_set_char(0, x, y, ch)

def dummy_draw_obj(obj):
    libtcod.console_set_char_foreground(0, obj.x, obj.y, libtcod.red)
    libtcod.console_set_char(0, obj.x, obj.y, obj.char)

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
        libtcod.console_set_default_foreground(new_console, libtcod.white)
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
        libtcod.console_set_default_foreground(tcod_cons,
                                                getattr(colors, msg.col))
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
