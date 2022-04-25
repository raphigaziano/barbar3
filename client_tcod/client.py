"""
Temporary client to interact with the barbarian game.

"""
from .constants import *
from .nw import Request
from .modes.base import ModeManager, InitMode
from .modes.run import RunMode
from .render import TcodRenderer
from .utils import closest_entities
from .clock import Clock


class BarbarClient:
    """
    Main client class.

    Interact with the game via its connection component,
    and interact with its current game mode by passing it game
    responses, and sending any request returned by the mode over the
    network.

    Also holds a renderer instance which will take care drawing to
    the screen, as well as the current gamestate (retrieved from
    game responses).

    """

    def __init__(self):
        self.game = None
        self.game_modes = None

        self.context = None
        self.renderer = None

        self.gamestate = None
        self.clock = Clock()
        self.gamelog = []
        self.bloodstains = []
        self.cursor_x, self.cursor_y = None, None
        self.path_from_cursor = []
        self.targeted_entity = None
        self.closest_actors = []

        self.con = None
        self.response = None

    @property
    def current_mode(self):
        return self.game_modes.current_mode

    def init(self, connection):
        """ Init all client systems and start the game. """
        self.con = connection
        self.renderer = TcodRenderer()
        self.context = self.renderer.init_tcod()
        self.renderer.init_consoles()

    def start(self, seed):
        """ Init mode manager and start the ui loop. """
        self.game_modes = ModeManager(self)
        self.game_modes.push(RunMode())
        self.send_request(Request.start({'seed': seed}))

        self.run()

    def render(self):
        """ Let the current mode handle rendering. """
        gs = self.gamestate
        gs.clock = self.clock
        gs.gamelog = self.gamelog
        gs.bloodstains = self.bloodstains
        gs.cursor_pos = (self.cursor_x, self.cursor_y)
        gs.path_from_cursor = self.path_from_cursor
        gs.closest_actors = self.closest_actors
        gs.targeted_entity = self.targeted_entity
        self.current_mode.render(gs, self.renderer)

    def send_request(self, r):
        """
        Send the passed request `r` and immediately process the
        response.

        """
        self.response = self.con.send(r)
        self.process_response()

    def process_response(self):
        """
        Preprocess a response (mainly by nabbing its gamesate)
        before passing it to the current mode.

        """
        status = self.response.status

        if status == 'OK':
            if self.response.gs:
                self.gamestate = self.response.gs
                self.closest_actors = closest_entities(
                    self.gamestate.actors,
                    self.gamestate.map['width'],
                    self.gamestate.visible_cells,
                    self.gamestate.distance_map)

        self.current_mode.process_response(self.response)

    def shutdown(self):
        """ Shutdown systems and exit. """
        self.con.close()
        self.renderer.shutdown_tcod()
        print('goodbye!')
        raise SystemExit()

    def run(self):
        """ Main client loop. """
        while not self.game_modes.done:
            self.clock.sync()
            self.render()
            request = self.game_modes.update()
            if request:
                self.send_request(request)

        return self.shutdown()
