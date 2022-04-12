from dataclasses import dataclass


@dataclass
class Particle:

    x: int
    y: int
    fg: tuple = (0, 0, 0)
    bg: tuple = (0, 0, 0)
    glyph: str = ' '
    lifetime: float = 200.0
