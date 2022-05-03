from barbarian.utils.rng import Rng
from . import builders


_MAP_BUILDERS = (
    builders.SimpleMapBuilder,
    builders.BSPMapBuilder,
    builders.BSPInteriorMapBuilder,
    builders.CellularAutomataMapBuilder,
    builders.DrunkardWalkBuilder.open_area,
    builders.DrunkardWalkBuilder.open_halls,
    builders.DrunkardWalkBuilder.winding_passages,
)


def get_map_builder(map_debug):
    """ Return a randomly chosen map builder. """
    # return builders.CellularAutomataMapBuilder(debug=map_debug)
    return Rng.dungeon.choice(_MAP_BUILDERS)(debug=map_debug)
