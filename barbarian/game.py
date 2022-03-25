"""
Main entry point / High level game logic.

"""
import logging
import logging.config

from barbarian import components
from barbarian import systems
from barbarian.state import GameState
from barbarian.world import World
from barbarian.spawn import spawn_player
from barbarian.actions import Action, ActionType, ActionError
from barbarian.events import Event, EventType
from barbarian.utils.rng import Rng

from barbarian.settings import MAP_W, MAP_H, MAP_DEBUG, LOGCONFIG


logger = logging.getLogger(__name__)


class EndTurn(Exception):
    """
    Raise this to abort a turn.

    Loop will keep running, but unprocessed actors for the current
    turn will be skipped.

    """


class Game:
    """
    Main game class.

    Manages the game loop and handle client requests and responses.

    """
    def __init__(self):
        self.is_running = False
        self.ticks = 1
        self.world = None
        self.player = None

        self.gameloop = None
        self.init_game()

        self.state = GameState()

    @property
    def current_level(self):
        """ Shotcut """
        return self.world.current_level

    @property
    def actors(self):
        """ Shotcut """
        return self.current_level.actors.all[:]

    @property
    def gs(self):
        """ Shotcut """
        return self.state.full

    ### Game Initialization ###
    ###########################

    def init_game(self):
        """
        Static initialization (ie, start systems that are not
        related to a sepcific run).

        """
        self.init_logging()
        components.init_components()
        systems.init_systems()

    @staticmethod
    def init_logging():
        """ Configure logger """
        logging.config.dictConfig(LOGCONFIG)
        logger.debug("Logger setup - Done")

    ### Run Initialization ###
    ##########################

    def start_game(self, seed=""):
        """
        Start a new run (ie initialize the game world and spwan the
        player on the first level.

        """
        self.init_rng(seed)
        self.state.clear()

        self.world = World(MAP_W, MAP_H)
        self.init_level()
        self.state.update(self)

        self.start_gameloop()

    @staticmethod
    def init_rng(s):
        """
        Initialize a root random genereted with the passed `seed`, as
        well as all specific generator that subsystems will require.

        """
        Rng.init_root(s)
        Rng.add_rng('dungeon')
        Rng.add_rng('spawn')

    @staticmethod
    def init_player(startx, starty):
        """ Spawn the player at the given position. """
        return spawn_player(startx, starty)

    def init_level(self):
        """ Build the first level. """
        level = self.world.new_level()
        self.world.insert_level(level)

        player_x, player_y = level.start_pos
        self.player = self.init_player(player_x, player_y)
        level.enter(self.player)

    ### Game loop ###
    #################

    def start_gameloop(self):
        self.gameloop = self._gameloop()
        return next(self.gameloop)

    def _gameloop(self):
        """
        Main loop.

        Iterate over all actors, have them chose an action, process it,
        and handle game events.

        If the chosen action is of type `REQUEST_INPUT`, this will
        yield and wait for input (ie: player turn) (see `take_turn`).

        Said input must be an action, which will be processed just like
        any other.

        """
        self.is_running = True
        while self.is_running:
            # Pre acting "static" stuff (increment hunger, process
            # status effects, etc...)
            pass

            # Game actions
            try:
                for actor in self.actors:
                    yield from self.take_turn(actor)
                    self.handle_events()
            except EndTurn:
                logger.debug("Turn ended prematurely")

            # Post acting stuff that should happen at the end of a turn
            Event.clear_queue()

            self.ticks += 1
            logger.debug('tick: %d', self.ticks)

    def take_turn(self, actor):
        """
        Handle the "chose action and process it" part of the game loop.

        Will loop recursively if an action is rejected so that `actor`
        can chose a new one. This allows the player to be informed
        of invalid input, but can get out of hand for ai actions.

        If a max recusrion error is catched, we simply abort the turn
        for this entity.

        """
        if (action := self.chose_action(actor)) is None:
            return

        # Player action: wait for input
        if action.type == ActionType.REQUEST_INPUT:
            self.state.update(self)
            action = yield

        # Loop until action is processed (so that processing can return
        # a new action).
        while not action.processed:
            try:
                action = self.process_action(action)
            except ActionError as e:
                logger.exception(e)
                return
            # Invalid action: request a new one.
            if action.processed and not action.valid:
                try:
                    yield from self.take_turn(actor)
                except RecursionError:
                    logger.critical(
                        "Maximum recursion limit reached while trying "
                        "to proccess action: %s", action)

    def chose_action(self, actor):
        """
        Delegate to the ai system to chose an action for `actor`.

        Said ai is respnsible for returning an input request if `actor`
        id the player.

        """
        # If the actor died earlier in the turn, then the level should
        # have removed it from its internal list already, while we're
        # still proccessing the current turn's list.
        if actor != self.current_level.actors[actor.pos.x, actor.pos.y]:
            if not actor.health.is_dead:
                logger.warning('actor %s does not belong to the current level', actor)
            return
        return systems.ai.tmp_ai(actor, self)

    def process_action(self, action):
        """
        Dispatch action to the appropriate system to handle it.

        Systems may return a new action to be processed (
        ie, move triggers an attack which in turn trigger damage...).

        Logs a warning if `action` could not be processed and keeps
        going.

        """
        logger.debug('Processing action: %s', action)

        new_action = None

        match action.type:

            case ActionType.IDLE:
                # No-op for now
                # action.accept(msg='\n'.join("TEST MULTILINE STRING".split()))
                # from string import ascii_letters
                # action.accept(msg=''.join(random.choice(ascii_letters) for _ in range(200)))
                action.accept()

            case ActionType.MOVE:
                new_action = systems.movement.move_actor(action, self.current_level)

            case ActionType.XPLORE:
                new_action = systems.movement.xplore(action, self.current_level)

            case ActionType.USE_PROP:
                new_action = systems.props.use_prop(action, self.current_level)

            case ActionType.OPEN_DOOR | ActionType.CLOSE_DOOR:
                systems.props.open_or_close_door(action, self.current_level)

            case ActionType.CHANGE_LEVEL:
                systems.movement.change_level(
                    action, self.world, self.player, debug=MAP_DEBUG)
                if action.valid:
                    raise EndTurn

            case ActionType.ATTACK:
                new_action = systems.combat.attack(action)

            case ActionType.INFLICT_DMG:
                new_action = systems.stats.inflict_damage(action)

        if new_action is None and not action.processed:
            logger.warning(
                'action of type %s could not be processed', action.type)
            action.reject()

        return new_action or action

    def handle_events(self):
        """ Process game events. """
        for e in Event.queue:
            if e.processed:
                continue
            if e.type == EventType.ACTOR_DIED:
                dead_actor = e.data['actor']
                # If we want a godmode, simply bypass this
                if dead_actor == self.player:
                    self.is_running = False
                    raise EndTurn
                e.processed = True
                self.current_level.actors.remove_e(dead_actor)

    ### NETWORK ###
    ###############

    @staticmethod
    def response(status, **data):
        """ Shortcut to build and send a response. """
        return {'status': status, **data}

    def receive_request(self, request):
        """
        Main entry point.

        Whehter called direcly or via server and network, this is
        what the client will call to send its input.

        Chose a handler method based on the request type (ie
        `process_<TYPE>_request` and pass it the request data. The
        handler's return value will be sent back to the caller.

        """
        rtype, rdata = request['type'], request['data']

        handler = getattr(self, f'process_{rtype.lower()}_request')
        if not handler:
            logger.warning('Received request of invalid type: %s', rtype)
            return {'status': 'error', 'err_code': 'INVALID_REQUEST'}

        return handler(rdata)

    def process_start_request(self, data):
        """ Process start request, ie start the game. """
        self.start_game(seed=data.get('seed', ''))
        return self.response('OK', gamestate=self.gs)

    def process_act_request(self, data):
        """ Process an action request. """
        data['actor'] = self.player
        if not self.is_running:
            return self.response('error', err_code='NOT_RUNNING')
        try:
            self.gameloop.send(Action.from_dict(data))
            return self.response('OK', gamestate=self.gs)
        except StopIteration:
            # Gameloop was aborted: yield the current gamestate so that
            # the client can know what happened
            self.state.update(self)
            return self.response('OK', gamestate=self.gs)
        except ActionError as e:
            msg = e.args[0]
            return self.response('error', err_code='INVALID_CMD', msg=msg)

    def process_get_request(self, d):
        """ Process a get request (ie return info to the client. """
        k = d['key']
        v = getattr(self, k)
        return self.response('OK', key=v)

    def process_set_request(self, d):
        """ Process a get request (ie set an internal valueà. """
        # Val is set in the module namespace (via globals()).
        # This should do for now, but we'll surely need a more robust
        # settings system in the long run...
        k = d['key']
        new_val = d['val']    # TODO: handle missing key error

        globals()[k] = new_val
        logger.debug('Set var %s to %s', k, new_val)

        return self.response('OK', key=k, val=new_val)
