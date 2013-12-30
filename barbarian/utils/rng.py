#! /usr/bin/env python
#-*- coding:utf-8 -*-
"""
rng.py
by Raphi

RNG related functions.

The standard library's random module is merged into this one, so all of its
functions are accessible without having to import it separately.

Tested with:
python 2.6.7 under linux-mint ... ok
python 3.2.2 under windows  7 ... ok

NOTE for libtcod users:
Some parts of the Doryen library (noise, heightmap, ...) uses [its own] RNG as
parameters. If you intend to use those functions, you must provide a RNG
created with the library.
(from the Doryen doc @
http://doryen.eptalys.net/data/libtcod/doc/1.5.0/random/index.html)

"""
# We *WANT* to merge the random module into this one, so stop pylint from
# complaining about it.
# pylint: disable=W0614
from random import *

# Exceptions
class RngError(Exception):
    pass
class DiceError(RngError, ValueError):
    pass


######################
##  BASIC WRAPPERS  ##
######################

# renaming the random.uniform function to a more explicit name
rand_double = uniform


def shuffle_copy(seq, gen=random):
    """
    Returns a shuffled copy of the passed sequence.

    Equivalent to the standard library's random.shuffle, except that
    the original sequence will not be affected.

    """
    return shuffle(seq[:], gen)


####################################
##  ROGUE/RPG SPECIFIC FUNCTIONS  ##
####################################

def coin_flip():
    """ Flip a coin & return either 1 or 0 (True or False). """
    return randint(0, 1)


def roll_dice(dice):
    """
    Dice Rolling function.

    The dice parameter must be a string of the classic RPG format:
    "1D12", "3d6", "2D4+2", "1D7"...
    Both "d" and D will work. The dice type doesn't have to exist in the
    real world (-> 1D7).

    """
    try:
        num, faces = dice.upper().split('D')
    except ValueError:
        raise DiceError("Invalid dice values: %s" % dice)
    try:
        faces, bonus = faces.split('+')
    except ValueError:
        try:
            faces, bonus = faces.split('-')
            bonus = '-%s' % bonus
        except ValueError:
            bonus = 0

    try:
        num, faces, bonus = int(num), int(faces), int(bonus)
    except ValueError:
        raise DiceError("Invalid dice values: %s" % dice)

    res = 0
    for _ in range(num):
        res += randint(1, faces)
    res += bonus
    if res < 1:
        res = 1

    return res


def check_roll(dice, dif):
    """
    Call `roll_dice` and returns a boolean indicating if the result was
    greater or equal to the specified dificulty.

    True -> Check passed, otherwise False.

    """
    return roll_dice(dice) >= dif


def random_table(table):
    """
    Pick a random item from the passed weighted table.

    Table must be a dictionnary where keys are the available items
    (any type should be ok), and their associated values are each item's
    chances of being selected.

    """
    if not isinstance(table, dict):
        raise TypeError("Random table must be a dictionary")

    roll = randint(0, sum(table.values()))
    running_sum = 0
    for item, chance in table.items():
        running_sum += chance
        if roll <= running_sum:
            return item


def randomize_items(item_types, aspects):
    """
    Associate random names & colors (aspects) from a list of
    (descr, color) tupples to corresponding item types (passed as a
    list).

    Returns a dict of type: (descr, color) items.

    """
    items_dict = {}
    # Copy the passed aspects list to avoid modifying the original
    aspects = aspects[:]

    for item in item_types:
        items_dict[item] = aspects.pop(randrange(0, len(aspects)))
    return items_dict

