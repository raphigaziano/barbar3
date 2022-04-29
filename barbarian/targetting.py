from dataclasses import dataclass
from enum import auto

from barbarian.utils.types import StringAutoEnum


class TargetMode(StringAutoEnum):
    """ Selection mode for actor and target. """
    USABLE = auto()
    ACTOR = auto()
    DIR = auto()
    POS = auto()


@dataclass
class TargettingInfo:
    """
    Data holder for targetting an action.

    """
    mode: TargetMode = TargetMode.USABLE

    def __post_init__(self):
        self.mode = TargetMode(self.mode)

    @property
    def requires_prompt(self):
        """
        Return whether or not `self.mode` requires additional data.

        """
        return self.mode in (TargetMode.DIR, TargetMode.POS)

