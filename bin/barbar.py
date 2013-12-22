#! /usr/bin/env python
"""
Launch script.

sys.path tweaks to simulate installed game.

"""
import os, sys
sys.path.append(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
)

from barbarian import barbar
