Simple python roguelike.

Inspired by various tutorials, and shamelessely stealing from
https://bfnightly.bracketproductions.com/ for map generation.

The goal is to experiment with architecture, more than creating a real game.

Install dependencies:
=====================

::

    # create venv
    $ pip install -r requirements.txt

Start server:
=============

::

    # activate venv
    $ python bin/server.py

Start client:
=============

::

    # activate venv
    $ python bin/simple_client_tcp.py

Base Game commands:
===================

rrow keys, numpad or vi keys to move around. Bump into monsters to attack, 
or into doors to open them. Press ? for more commands.

Escape to quit.

Debug commands:
---------------

- `Alt - n` to regen the current level
- `Alt - d` to activate map debug mode
        (this shows map generation when creating a new map)
- `Alt - r` rerun map debug on the current level

- `Alt - x` to show the whole map
- `Alt - f` to ignore fov
- `Alt - p` to show pathing map
- `Alt - v` to show spawn regions
