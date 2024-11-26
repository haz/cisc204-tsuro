

def rotate_tile_multiple(_edges, n):
    edges = _edges[:]
    for _ in range(n):
        edges = rotate_tile(edges)
    return edges

def rotate_tile(edges):
    return [(((x+1) % 8)+1, ((y+1) % 8)+1) for (x,y) in edges]

def display_solution(S, only_tile_placement=False):
    true_props = set()
    for k in S:
        if S[k] and (not only_tile_placement or '@' in str(k)):
            true_props.add(str(k))
            # print(k)
    print("\n".join(sorted(true_props)))

def extract_path(S, Reachable, MAX_HOPS):
    paths = [[[], []], [[], []]]
    for k in S:
        if k.__class__.__name__ == "LocationConnection":
            if S[k]:
                i = int(k.location[1])-1
                j = int(k.location[2])-1
                if any([S[Reachable(k.location, k.edge1, hop)] for hop in range(MAX_HOPS+1)]) and \
                   any([S[Reachable(k.location, k.edge2, hop)] for hop in range(MAX_HOPS+1)]):
                    paths[i][j].append((k.edge1, k.edge2))

    return paths

def extract_tile_placement(S, TILES):
    solution = [[[], []], [[], []]]
    for k in S:
        if k.__class__.__name__ == "Location" and S[k]:
            i = int(k.location[1])-1
            j = int(k.location[2])-1
            solution[i][j] = TILES[k.tile]

    return solution
