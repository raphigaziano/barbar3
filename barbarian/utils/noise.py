"""
Helpers for noise generation.

"""
from pyfastnoiselite.pyfastnoiselite import (
    FastNoiseLite, NoiseType,
    CellularDistanceFunction,
    CellularReturnType,
)


CELLULAR_FREQ = 0.08

def get_cellular_voronoi_noise_generator(rng):
    """
    Configure and return a noise generator for voronoi zones.

    Used to generate spawn zones an maps without rooms.

    """
    noise = FastNoiseLite(rng.randint(0, 65536))
    noise.noise_type = NoiseType.NoiseType_Cellular
    noise.frequency = CELLULAR_FREQ
    noise.cellular_distance_function = (
        CellularDistanceFunction.CellularDistanceFunction_Manhattan)
    noise.cellular_return_type = CellularReturnType.CellularReturnType_CellValue

    return noise
