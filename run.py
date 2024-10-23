
import pprint


from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

from examples import example1
from utils import rotate_tile_multiple, display_solution


# Encoding that will store all of your constraints
E = Encoding()



ORIENTATIONS = list('NESW')


TILES = {}
TIDS = set()

LOCATIONS = ['l11', 'l12', 'l21', 'l22']



# Build the tiles with the 4 rotations in mind
tid = 1
rid = 0
for tile in example1['tiles']:
    TIDS.add(tid)
    for _ in range(4):
        TILES[f't{tid}{ORIENTATIONS[rid % 4]}'] = rotate_tile_multiple(tile, rid%4)
        rid += 1
    tid += 1


# import pprint
# pprint.pprint(TILES)
# exit()

# New proposition to say two edges (1->8) are connected or not for a particular tile
@proposition(E)
class TileConnection(object):
    def __init__(self, tile, edge1, edge2) -> None:
        assert tile in TILES
        assert edge1 in range(1,9)
        assert edge2 in range(1,9)
        self.tile = tile
        self.edge1 = edge1
        self.edge2 = edge2

    def _prop_name(self):
        return f"({self.tile}: {self.edge1} -> {self.edge2})"


# Similarly, create a LocationConnection
@proposition(E)
class LocationConnection(object):
    def __init__(self, location, edge1, edge2) -> None:
        assert location in LOCATIONS
        assert edge1 in range(1,9)
        assert edge2 in range(1,9)
        self.location = location
        self.edge1 = edge1
        self.edge2 = edge2

    def _prop_name(self):
        return f"({self.location}: {self.edge1} -> {self.edge2})"


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


    # A tile is placed in exactly one configuration somewhere on the board
    for t in TIDS:
        location_propositions = []
        tids = [f't{t}{o}' for o in ORIENTATIONS]
        for l in LOCATIONS:
            for tid in tids:
                location_propositions.append(Location(tid, l))

        constraint.add_exactly_one(E, location_propositions)

    # For any given location, at most one tile is placed there
    for location in LOCATIONS:
        tile_at_props = []
        for tile in TILES:
            tile_at_props.append(Location(tile, location))
        constraint.add_at_most_one(E, tile_at_props)


    #   { TILE CONNECTIONS }

    # Tiles we have, have their connections set
    for tile, edges in TILES.items():
        for edge1, edge2 in edges:
            E.add_constraint(TileConnection(tile, edge1, edge2))

    # Connections are symmetric
    for tile, edges in TILES.items():
        for edge1, edge2 in edges:
            E.add_constraint(TileConnection(tile, edge1, edge2) >> TileConnection(tile, edge2, edge1))

    # Connections are to exactly one other
    for tile in TILES:
        for edge1 in range(1, 9):
            possible_connections = []
            for edge2 in range(1, 9):
                if edge1 == edge2:
                    continue
                possible_connections.append(TileConnection(tile, edge1, edge2))
            constraint.add_exactly_one(E, possible_connections)

    # TODO: Make sure no self-loops are allowed



    #   { LOCATION CONNECTIONS }

    # Connections are symmetric
    for location in LOCATIONS:
        for edge1 in range(1, 9):
            for edge2 in range(1, 9):
                E.add_constraint(LocationConnection(location, edge1, edge2) >> LocationConnection(location, edge2, edge1))


    # For every location and edge on it, there is at most one connection
    for location in LOCATIONS:
        for edge1 in range(1, 9):
            possible_connections = []
            for edge2 in range(1, 9):
                if edge1 == edge2:
                    continue
                possible_connections.append(LocationConnection(location, edge1, edge2))
            constraint.add_at_most_one(E, possible_connections)

    # If a tile is placed at a location, then the tile connections force the location connections to be the same
    for location in LOCATIONS:
        for edge1 in range(1, 9):
            for edge2 in range(1, 9):
                for tile in TILES:
                    E.add_constraint((Location(tile, location) & TileConnection(tile, edge1, edge2)) >> LocationConnection(location, edge1, edge2))

    # TODO: If there is no tile at a location, then there are no connections on that location

    # TODO: Make sure no self-loops are allowed




    # TODO: Neighbouring tiles have their matching edges connected

    return E




if __name__ == "__main__":

    T = example_theory()


    T = T.compile()

    print()

    S = T.solve()
    display_solution(S)

    # E.introspect(S)


    # print("\nSatisfiable: %s" % T.satisfiable())
    # print("# Solutions: %d" % count_solutions(T))
    # print("   Solution: %s" % T.solve())


    print()
