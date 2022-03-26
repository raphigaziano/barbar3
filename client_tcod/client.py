"""
Temporary client to interact with the barbarian game.

"""
from .constants import *
from .nw import Request
from .modes.base import ModeManager, InitMode
from .modes.run import RunMode
from .render import TcodRenderer
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
        self.game_modes.push(InitMode())
        self.send_request(Request.start({'seed': seed}))

        self.run()

    def render(self):
        """ Let the current mode handle rendering. """
        self.gamestate.clock = self.clock
        self.current_mode.render(self.gamestate, self.renderer)

    def send_request(self, r):
        """
        Send the passed request `r` and immediately process the
        response.

        """
        self.response = self.con.send(r)
        self.process_response()

    def process_request(self, r):
        """
        Preprocess a request before sending it.

        Some requests (called `client` requests) will be handled
        by the client and not sent to the game: this is where
        we handle this distinction.

        """
        if r['type'] in ('ACT', 'GET', 'SET'):
            self.send_request(r)
        # Special case for client requests
        else:
            # First see if the client has a hendler for this
            cmd = r['data']['cmd']
            handler = getattr(self, f"cmd_{cmd}", None)
            if handler:
                handler(r['data'])
            # If not, then delegate to the current mode
            else:
                self.current_mode.process_request(r)

    def process_response(self):
        """
        Preprocess a response (mainly by nabbing its gamesate)
        before passing it to the current mode.

        """
        status = self.response.status

        if status == 'OK':
            if self.response.gs:
                self.gamestate = self.response.gs

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
            self.render()
            request = self.game_modes.update()
            if request:
                self.process_request(request)
            self.clock.sync()

        return self.shutdown()
