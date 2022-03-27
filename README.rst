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

Game commands:
==============

- Arrow keys, numpad or vi keys to move around.
- `,` or Keypad 5: skip turn
- `<`: use stairs (up)
- `>`: use stairs (down)

- `I`: Show inventory
- `G`: Get item
- `D`: Drop item

- `Ctrl - o`: Manually open door
- `Ctrl - c`: Manually close door

- `Shift - <movment key (see above)>`: move until blocked or hostile gets in view
- `Ctrl - x`: autoexplore

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
