# -*- coding: utf8 -*-
"""
barbarian.log.py
================

Logging initialisation & custom loggers definition.

"""
import sys
import logging

from barbarian import gui

class BarbarGuiHandler(logging.StreamHandler):

    """ Custom Handler to send colorized log messages to our GUI console. """

    LEVEL_COLORS = {
        'DEBUG': 'white',
        'INFO': 'yellow',
        'WARN': 'orange',
        'WARNING': 'orange',
        'ERROR': 'red',
        'FATAL': 'red',
        'CRITICAL': 'red',
    }

    def emit(self, record):
        """
        Mimick the base StreamHandler method, with level dependant
        message coloring & less error handling.

        """
        try:
            msg = self.format(record)
            fs = "%s\n"
            self.stream.write(fs % msg, self.LEVEL_COLORS[record.levelname])
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def init(logger_name):
    """ Root Logger Setup. """
    logger = logging.getLogger(logger_name)
    logger.level = logging.DEBUG
    console_handler = logging.StreamHandler(sys.stderr)
    # console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    )

    barbargui_handler = BarbarGuiHandler(gui.manager.debug_console)
    barbargui_handler.setLevel(logging.DEBUG)
    barbargui_handler.setFormatter(
        logging.Formatter('[%(levelname)s] %(message)s')
    )

    logger.addHandler(console_handler)
    logger.addHandler(barbargui_handler)

    logger.debug("Logger setup - Done")
