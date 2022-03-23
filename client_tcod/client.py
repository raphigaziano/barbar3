"""
Temporary client to interact with the barbarian game.

"""
from .constants import *
from .nw import Request
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
        self.current_mode = RunMode(self)

        self.context = None
        self.renderer = None

        self.gamestate = None
        self.clock = Clock()

        self.con = None
        self.response = None

    def init(self, connection, seed):
        """ Init all client systems and start the game. """
        self.con = connection
        self.renderer = TcodRenderer()
        self.context = self.renderer.init_tcod()
        self.renderer.init_consoles()

        self.send_request(Request.start({'seed': seed}))

    def start(self, connection, seed):
        """ Init the client (see above) and start the ui loop. """
        self.init(connection, seed)
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

    def cmd_shutdown(self, _):
        """ Shutdown systems and exit. """
        self.con.close()
        self.renderer.shutdown_tcod()
        print('goodbye!')
        raise SystemExit()

    def run(self):
        """ Main client loop. """
        while True:
            self.render()
            request = self.current_mode.ui_events.handle(self.context)
            if request:
                self.process_request(request)
            self.clock.sync()
