
import pprint


from bauhaus import Encoding, proposition, constraint, And, Or
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

LOCATIONS = []
LOCATION_GRID = {}

def generate_locations(rows, cols):

    global LOCATIONS, LOCATION_GRID
    assert rows < 10, "Can only do a board of up to size 9"
    assert cols < 10, "Can only do a board of up to size 9"

    for row in range(1, rows+1):
        LOCATION_GRID[row] = {}
        for col in range(1, cols+1):
            LOCATIONS.append(f'l{row}{col}')
            LOCATION_GRID[row][col] = f'l{row}{col}'




# These are the 8 locations around the outside (4 sides) of a tile or location.
#  They go from the left North clockwise around and end at the top West.

#     1   2
#   +-------+
# 8 |       | 3
#   |       |
# 7 |       | 4
#   +-------+
#     6   5


EDGES = list(range(1, 9))




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
        assert edge1 in EDGES
        assert edge2 in EDGES
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
        assert edge1 in EDGES
        assert edge2 in EDGES
        self.location = location
        self.edge1 = edge1
        self.edge2 = edge2

    def _prop_name(self):
        return f"({self.location}: {self.edge1} -> {self.edge2})"

# Cross-location connections (between two neighbouring locations)
@proposition(E)
class CrossLocationConnection(object):
    def __init__(self, location1, location2, edge1, edge2) -> None:
        assert location1 in LOCATIONS, f"Location {location1} does not exist!"
        assert location2 in LOCATIONS, f"Location {location2} does not exist!"
        assert edge1 in EDGES
        assert edge2 in EDGES
        self.location1 = location1
        self.location2 = location2
        self.edge1 = edge1
        self.edge2 = edge2

    def _prop_name(self):
        return f"({self.location1}@{self.edge1}) -> {self.location2}@{self.edge2})"

@proposition(E)
class Location(object):
    def __init__(self, tile, location) -> None:
        assert tile in TILES
        assert location in LOCATIONS
        self.tile = tile
        self.location = location

    def _prop_name(self):
        return f"({self.tile} @ {self.location})"


def test_no_connections_when_no_tile():
    E.add_constraint(LocationConnection("l22", 1, 2))
    E.add_constraint(Location("t1N", "l11"))
    E.add_constraint(Location("t2N", "l12"))
    E.add_constraint(Location("t3N", "l21"))



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
        for edge1 in EDGES:
            possible_connections = []
            for edge2 in EDGES:
                if edge1 == edge2:
                    continue
                possible_connections.append(TileConnection(tile, edge1, edge2))
            constraint.add_exactly_one(E, possible_connections)

    # Make sure no self-loops are allowed
    for tile in TILES:
        for edge in EDGES:
            E.add_constraint(~TileConnection(tile, edge, edge))



    #   { LOCATION CONNECTIONS }

    # Connections are symmetric
    for location in LOCATIONS:
        for edge1 in EDGES:
            for edge2 in EDGES:
                E.add_constraint(LocationConnection(location, edge1, edge2) >> LocationConnection(location, edge2, edge1))


    # For every location and edge on it, there is at most one connection
    for location in LOCATIONS:
        for edge1 in EDGES:
            possible_connections = []
            for edge2 in EDGES:
                if edge1 == edge2:
                    continue
                possible_connections.append(LocationConnection(location, edge1, edge2))
            constraint.add_at_most_one(E, possible_connections)

    # If a tile is placed at a location, then the tile connections force the location connections to be the same
    for location in LOCATIONS:
        for edge1 in EDGES:
            for edge2 in EDGES:
                for tile in TILES:
                    E.add_constraint((Location(tile, location) & TileConnection(tile, edge1, edge2)) >> LocationConnection(location, edge1, edge2))

    # If there is no tile at a location, then there are no connections on that location
    # NOTE: This constraint was confirmed & tested with test_no_connections_when_no_tile()
    for location in LOCATIONS:
        all_connections_for_location = []
        for edge1 in EDGES:
            for edge2 in EDGES:
                all_connections_for_location.append(~LocationConnection(location, edge1, edge2))

        all_tiles_at_location = []
        for tile in TILES:
            all_tiles_at_location.append(~Location(tile, location))

        E.add_constraint(And(all_tiles_at_location) >> And(all_connections_for_location))


    # Make sure no self-loops are allowed
    for location in LOCATIONS:
        for edge in EDGES:
            E.add_constraint(~LocationConnection(location, edge, edge))

    # TODO: Neighbouring locations have their matching edges connected
    # Example with two tiles side by side:
    #     1   2
    #   +-------+       +-------+
    # 8 |       | 3   8 |       |
    #   |       |       |       |
    # 7 |       | 4   7 |       |
    #   +-------+       +-------+
    #     6   5
    num_rows = len(LOCATION_GRID)
    num_cols = len(LOCATION_GRID[1])

    # Horizontal connections
    for col in range(1, num_cols):
        for row in range(1, num_rows+1):
            loc1 = f"l{row}{col}"
            loc2 = f"l{row}{col+1}"
            E.add_constraint(CrossLocationConnection(loc1, loc2, 3, 8))
            E.add_constraint(CrossLocationConnection(loc1, loc2, 4, 7))

    # TODO: We'll need symmetric connections
    # TODO: Do the vertical ones as well
    # TODO: Create all the other location/edge pairs to say that they are /not/ connected
    #           I.e., go through all loc1 and loc2 and edge1 and edge 2


    # TODO: Start on the full path propositions and constraints

    return E




if __name__ == "__main__":

    generate_locations(2, 2)

    T = example_theory()
    # test_no_connections_when_no_tile()

    T = T.compile()

    print()

    S = T.solve()
    if S:
        display_solution(S, only_tile_placement=True)
    else:
        print("No solution!!")

    # E.introspect(S)


    # print("\nSatisfiable: %s" % T.satisfiable())
    # print("# Solutions: %d" % count_solutions(T))
    # print("   Solution: %s" % T.solve())


    print()
