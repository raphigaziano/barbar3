# -*- coding: utf8 -*-
"""
barbarian.log.py
================

Logging initialisation & custom loggers definition.

"""
import sys
import logging

from barbarian import gui

def init(logger_name):
    """ Root Logger Setup. """
    logger = logging.getLogger(logger_name)
    logger.level = logging.DEBUG
    logger.addHandler(logging.StreamHandler(sys.stderr))
    logger.addHandler(logging.StreamHandler(gui.manager.debug_console))

    logger.debug("Logger setup - Done")
