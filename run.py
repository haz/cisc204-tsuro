
import pprint


from bauhaus import Encoding, proposition, constraint, And, Or
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

from examples import example1 as EXAMPLE
from utils import rotate_tile_multiple, display_solution, extract_path, extract_tile_placement
from viz import draw_2by2_tiles


# Encoding that will store all of your constraints
E = Encoding()



ORIENTATIONS = list('NESW')

MAX_HOPS = 17

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
for tile in EXAMPLE['tiles']:
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
        return f"({self.location1}@{self.edge1} -> {self.location2}@{self.edge2})"

@proposition(E)
class Location(object):
    def __init__(self, tile, location) -> None:
        assert tile in TILES
        assert location in LOCATIONS
        self.tile = tile
        self.location = location

    def _prop_name(self):
        return f"({self.tile} @ {self.location})"

@proposition(E)
class Reachable(object):
    def __init__(self, location, edge, k):
        assert location in LOCATIONS, f"Location {location} does not exist!"
        assert edge in EDGES, f"Edge {edge} does not exist!"
        assert k in range(0, MAX_HOPS+1), f"Invalid number of hops {k}"
        self.location = location
        self.edge = edge
        self.k = k

    def _prop_name(self):
        return f"R({self.location}@{self.edge}, {self.k})"


# Created to make sure that no connections are made on a location with no tile (this successfully makes the example unsat)

def test_no_connections_when_no_tile():
    E.add_constraint(LocationConnection("l22", 1, 2))
    E.add_constraint(Location("t1N", "l11"))
    E.add_constraint(Location("t2N", "l12"))
    E.add_constraint(Location("t3N", "l21"))


# Found that R(l11, 3, 1) was not being set true, but it should be because of the tile that's there.
#  Force it to be true, and see if it's possible.
#   If UNSAT, then it means we weren't able to make that configuration.
#   If SAT, then the constraints were being applied correctly.

#  HYPOTHESIS: I need to force the same example that the viz is using
#  CONCLUSION: Confirmed! It was unsat when I tried forcing, and that's because the example had a forced starting location.

def test_reachable_forced_path():
    E.add_constraint(Reachable("l11", 8, 0))
    E.add_constraint(Reachable("l11", 3, 1))


# A starting tile position that caused a bad viz (documented in the report)

def test_broken_connections():
    E.add_constraint(Location("t3S", "l11"))



# Wanted and example (example2) that would force the longest path possible
def test_force_long_plan():
    E.add_constraint(Reachable('l11', 2, 17))
    E.add_constraint(Reachable('l11', 3, 8))


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

    # Neighbouring locations have their matching edges connected
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

    connected_locations = set()

    # Horizontal connections
    for col in range(1, num_cols):
        for row in range(1, num_rows+1):
            loc1 = f"l{row}{col}"
            loc2 = f"l{row}{col+1}"
            E.add_constraint(CrossLocationConnection(loc1, loc2, 3, 8))
            E.add_constraint(CrossLocationConnection(loc1, loc2, 4, 7))
            E.add_constraint(CrossLocationConnection(loc2, loc1, 8, 3))
            E.add_constraint(CrossLocationConnection(loc2, loc1, 7, 4))
            connected_locations.add(f"{loc1}-3-{loc2}-8")
            connected_locations.add(f"{loc1}-4-{loc2}-7")
            connected_locations.add(f"{loc2}-8-{loc1}-3")
            connected_locations.add(f"{loc2}-7-{loc1}-4")


    # Vertical connections
    for col in range(1, num_cols+1):
        for row in range(1, num_rows):
            loc1 = f"l{row}{col}"
            loc2 = f"l{row+1}{col}"
            E.add_constraint(CrossLocationConnection(loc1, loc2, 6, 1))
            E.add_constraint(CrossLocationConnection(loc1, loc2, 5, 2))
            E.add_constraint(CrossLocationConnection(loc2, loc1, 1, 6))
            E.add_constraint(CrossLocationConnection(loc2, loc1, 2, 5))
            connected_locations.add(f"{loc1}-6-{loc2}-1")
            connected_locations.add(f"{loc1}-5-{loc2}-2")
            connected_locations.add(f"{loc2}-1-{loc1}-6")
            connected_locations.add(f"{loc2}-2-{loc1}-5")

    # Create all the other location/edge pairs to say that they are /not/ connected
    #           I.e., go through all loc1 and loc2 and edge1 and edge 2
    for loc1 in LOCATIONS:
        for loc2 in LOCATIONS:
            for edge1 in EDGES:
                for edge2 in EDGES:
                    if f"{loc1}-{edge1}-{loc2}-{edge2}" not in connected_locations:
                        E.add_constraint(~CrossLocationConnection(loc1, loc2, edge1, edge2))


    # You can get to the starting spot in 0 hops, but nowhere else in 0 hops
    E.add_constraint(Reachable(EXAMPLE['start']['location'], EXAMPLE['start']['edge'], 0))
    for loc in LOCATIONS:
        for edge in EDGES:
            if loc != EXAMPLE['start']['location'] or edge != EXAMPLE['start']['edge']:
                E.add_constraint(~Reachable(loc, edge, 0))

    # If you can get to a location in k hops, then you can get to a neighbour of it in k+1 hops

    def compute_connected(loc1, edge1, loc2, edge2):
        if loc1 == loc2:
            return LocationConnection(loc1, edge1, edge2)
        else:
            return CrossLocationConnection(loc1, loc2, edge1, edge2)

    for k in range(0, MAX_HOPS):
        for loc1 in LOCATIONS:
            for edge1 in EDGES:
                for loc2 in LOCATIONS:
                    for edge2 in EDGES:
                        E.add_constraint((Reachable(loc1, edge1, k) & compute_connected(loc1, edge1, loc2, edge2)) >> Reachable(loc2, edge2, k+1))

    # If you set Reachable(l, e, k) to be true, then there must be something connected to it that is reachable in k-1 hops
    for k in range(1, MAX_HOPS+1):
        for loc in LOCATIONS:
            for edge in EDGES:
                possible_connections = []
                for loc2 in LOCATIONS:
                    for edge2 in EDGES:
                        possible_connections.append(compute_connected(loc2, edge2, loc, edge) & Reachable(loc2, edge2, k-1))
                E.add_constraint(Reachable(loc, edge, k) >> Or(possible_connections))

    return E




if __name__ == "__main__":

    generate_locations(2, 2)

    T = example_theory()

    # test_no_connections_when_no_tile()
    # test_reachable_forced_path()
    # test_broken_connections()
    # test_force_long_plan()

    # E.add_constraint(Location("t1N", "l11"))
    # E.add_constraint(Location("t2N", "l12"))
    # E.add_constraint(Location("t3N", "l21"))

    T = T.compile()

    print()

    S = T.solve()
    if S:
        display_solution(S, only_tile_placement=True)
        tile_placement = extract_tile_placement(S, TILES)
        path = extract_path(S, Reachable, MAX_HOPS)
        draw_2by2_tiles(tile_placement, path=path).show()
    else:
        print("No solution!!")

    # E.introspect(S)


    # print("\nSatisfiable: %s" % T.satisfiable())
    # print("# Solutions: %d" % count_solutions(T))
    # print("   Solution: %s" % T.solve())


    print()
