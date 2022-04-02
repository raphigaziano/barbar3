""" Random generators and helpers """
import sys
import random
import logging


logger = logging.getLogger(__name__)


# Exceptions
class RngError(Exception):
    pass


class RngDiceError(RngError, ValueError):
    pass


class _Rng(random.Random):
    """
    Extend the regular random.Random class with some rogue/rpg
    typical helpers.

    """

    def seed(self, s, *args, **kwargs):
        """
        Wrap the regular seed method and store the seed (mainly useful
        for testing).

        """
        self.initial_seed = s
        return super().seed(s, *args, **kwargs)

    def shuffle_copy(self, seq):
        """
        Returns a shuffled copy of the passed sequence.

        Equivalent to the standard library's random.shuffle, except that
        the original sequence will not be affected.

        """
        return self.shuffle(seq[:])

    def coin_toss(self):
        """ Flip a coin & return either 1 or 0 (True or False). """
        return self.randint(0, 1)

    def roll_dice(self, n, faces, mod):
        """
        Roll a dice and return the roll result.

        params:
            n:      Number of dice to roll
            faces:  Number of faces for each dice
            mod:    A bonus or malus (int) applied to the whole roll

        """
        res = 0
        for _ in range(n):
            res += self.randint(1, faces)
        res += mod

        return max(1, res)

    def roll_dice_str(self, dice_string):
        """
        Parse a diceroll string and roll the corresponding dice.

        The dice_string parameter must be a string of the classic RPG format:
        "1D12", "3d6", "2D4+2", "1D7"...
        Both "d" and D will work. The dice type doesn't have to exist in the
        real world (-> 1D7).

        """
        # TODO: just use a regex to find our values.
        try:
            num, faces = dice_string.upper().split('D')
        except (ValueError, AttributeError) as e:
            raise RngDiceError(
                f"Invalid dice string: {dice_string}") from e
        try:
            faces, mod = faces.split('+')
        except ValueError:
            try:
                faces, mod = faces.split('-')
                mod = f'-{mod}'
            except ValueError:
                mod = 0

        try:
            num, faces, mod = int(num), int(faces), int(mod)
        except ValueError as e:
            raise RngDiceError(f"Invalid dice string: {dice_string}") from e

        return self.roll_dice(num, faces, mod)

    def roll_table(self, table):
        """
        Return a random object from the passed weighted table.

        Table should be an iterable of (weight, obj) tupples.

        """
        if not table:
            raise RngError("Can't roll on an emmpty table.")

        total_weight = sum(w for w, _ in table)

        try:
            roll = self.uniform(1, total_weight)
        except ValueError:
            raise RngError(f'Invalid weights (total={total_weight})')

        running_sum = 0
        for weight, obj in table:
            running_sum += weight
            if roll <= running_sum:
                logger.debug(
                    '%d - %d - %d - %s', roll, running_sum, total_weight, obj)
                return obj

        raise RngError(f'Could not pick object from table: {table}')


class _RngMeta(type):
    """
    Enables attribute delegation for the Rng class.

    See its docs below for more info.

    """

    _rngs = {}
    _root = None

    @classmethod
    def __getattr__(cls, attr_name):

        # access a named rng
        if attr_name in cls._rngs:
            return cls._rngs[attr_name]

        # Try and delegate to the root rng
        if cls._root:
            return getattr(cls._root, attr_name)

        # Try and delegate to the random module (maybe the user
        # doesn't care about manging several rngs and just wants to
        # use the helper class)
        return getattr(random, attr_name)

    # Guarantee classes using this metaclass won't shadow our vars:

    @property
    def rngs(cls):
        return _RngMeta._rngs

    @property
    def root(cls):
        return _RngMeta._root

    @root.setter
    def root(cls, val):
        _RngMeta._root = val


class Rng(metaclass=_RngMeta):
    """
    Facade for the random module.

    Acts as a namespace or a static class, and can hold one or several
    instances of our custom _Rng generator (se above).

    Held instance can be named, which requires creating them through
    the `add_rng(rng_name, seed)` method. Thos can then be accessed
    directly from the class, ie:

    >>> Rng.add_rng('my_fancy_generator')
    >>> Rng.add_rng('and_another_one')
    >>> Rng.my_fancy_generator.randint(0, 20)
    >>> Rng.and_another_one.choice([1, 2, 3])

    Defining a root generator will allow calling that instance's
    method directly from the class:

    >>> Rng.init_root()
    >>> Rng.randint(1, 20)

    If no root generator is defnined, then methods will be delegated
    to the random module (you'll lose access to the custom helpers
    defined in _Rng.

    """

    @classmethod
    def _get_seed(cls, s=""):
        """
        Seeds passed from the client will be strings, while seeds
        generated by randint (as happen if no inital seed is passed)
        will be ints, which cause confusion when copying and pasting.

        Enforcing a str type for all seeds should solve this problem.

        """
        return s or str(cls.randint(0, sys.maxsize))

    @classmethod
    def init_root(cls, seed=""):
        """
        Initialize a <root> generator with the given seed, which will
        be used if no specific rng is requested. If this is not called,
        then random method will use the default `Random` class defined in the
        `random` module.

        Setting up an explicit root generator is optional, but recommended.

        """
        # Do we want to allow reinitializing the root rng ?
        # If so, then it's causing problems as long as the server
        # keeps holding on a single instance of the game object
        # (ie every session reuse the same game, and hence the same
        # root rng)
        #
        # if cls.root is not None:
        #     return

        cls.root = None
        s = seed or cls._get_seed(seed)
        cls.root = _Rng(s)

        logger.info('Root Rng initialized with seed: %s', s)

    @classmethod
    def add_rng(cls, rng_name, seed=""):
        """
        Add a named generator that interested parties can access
        via `Rng.<NAME>`

        """
        s = seed or cls._get_seed(seed)
        cls.rngs[rng_name] = _Rng(s)

        logger.info('Rng[%s] initialized with seed: %s', rng_name, s)
