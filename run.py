
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()



ORIENTATIONS = list('NSEW')
TILES = ['t1', 't2']
LOCATIONS = ['l11', 'l12', 'l21', 'l22']


@proposition(E)
class Configuration(object):
    def __init__(self, tile, orientation) -> None:
        assert tile in TILES
        assert orientation in ORIENTATIONS
        self.tile = tile
        self.orientation = orientation

    def _prop_name(self):
        return f"config({self.tile}={self.orientation})"



@proposition(E)
class Location(object):
    def __init__(self, tile, location) -> None:
        assert tile in TILES
        assert location in LOCATIONS
        self.tile = tile
        self.location = location

    def _prop_name(self):
        return f"({self.tile} @ {self.location})"

def example_theory():

    # for every tile, it must be in exactly one configuration
    for t in TILES:
        all_orientations = []
        for o in ORIENTATIONS:
            all_orientations.append(Configuration(t,o))

        constraint.add_exactly_one(E, all_orientations)

    for t in TILES:
        for l in LOCATIONS:
            print(Location(t, l))

    x = Location('t1', 'l12')
    y = Location('t1', 'l12')

    print(x == y)

    return E


if __name__ == "__main__":

    T = example_theory()


    T = T.compile()

    print()

    S = T.solve()
    # E.introspect(S)


    # print("\nSatisfiable: %s" % T.satisfiable())
    # print("# Solutions: %d" % count_solutions(T))
    # print("   Solution: %s" % T.solve())


    print()
