# -*- coding: utf8 -*-
"""
barbarian.log.py
================

Logging initialisation & custom loggers definition.

"""
import sys
import logging

def init(logger_root_name):
    """ Root Logger Setup """
    logger = logging.getLogger(logger_root_name)
    logger.level = logging.DEBUG
    logger.addHandler(logging.StreamHandler(sys.stderr))
