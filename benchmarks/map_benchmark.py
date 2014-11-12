from timeit import timeit


setup_code = """
from barbarian.map import Map
cells = [
    'a', 'b', 'c', 'd', 'e', 'a', 'b', 'c', 'd', 'e',
    'f', 'g', 'h', 'i', 'j', 'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 'r', 't', 'p', 'q', 'r', 'r', 't',
    'u', 'v', 'w', 'x', 'y', 'u', 'v', 'w', 'x', 'y',
    'a', 'b', 'c', 'd', 'e', 'a', 'b', 'c', 'd', 'e',
    'f', 'g', 'h', 'i', 'j', 'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 'r', 't', 'p', 'q', 'r', 'r', 't',
    'u', 'v', 'w', 'x', 'y', 'u', 'v', 'w', 'x', 'y',
]

m = Map(10, 10, cells)
"""

print 'small subset: ',
print timeit('m.slice(2, 2, 2, 2)', setup=setup_code)

print 'large subset: ',
print timeit('m.slice(1, 1, 9, 9)', setup=setup_code)


