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

tcod_consoles = {
    'event_console': libtcod.console_new(80, 40),
    'debug_console': libtcod.console_new(70, 40)
}
def dummy_draw_console(con, tcod_cons, x, y, blit_on=0):
    """
    Blits the widget to the console passed as parameter (defaults to
    the root console), with its top-left corner at the specified
    x:y position.
    This is the bare minimum any widget will have to do to draw
    itself.
    """
    if not con.visible:
        return
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
    libtcod.console_set_default_foreground(tcod_cons, libtcod.white)
    libtcod.console_set_default_background(tcod_cons, libtcod.blue)
    libtcod.console_print_frame(tcod_cons, 0, 0, con.w, con.h,
                                False, # BACKGROUND_FLAG, title
                                )
    # /TEMPO!

    # for i, msg in enumerate(con.msgs[-(8+offset):-(offset)]):
    for i, msg in enumerate(con.last_msgs):
        libtcod.console_set_default_foreground(tcod_cons,
                                                getattr(colors, msg.col))
        libtcod.console_print_rect(tcod_cons, 1, 1+i, con.w, con.h, msg.txt)

    libtcod.console_blit(tcod_cons, 0, 0, con.w, con.h, blit_on, x, y,)
                        # self.forealpha, self.backalpha)
    # libtcod.console_flush()

def flush():
    libtcod.console_flush()

def clear(con=0):
    libtcod.console_clear(con)
