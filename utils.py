
def rotate_tile_multiple(_edges, n):
    edges = _edges[:]
    for _ in range(n):
        edges = rotate_tile(edges)
    return edges

def rotate_tile(edges):
    return [(((x+1) % 8)+1, ((y+1) % 8)+1) for (x,y) in edges]


def display_solution(S):
    for k in S:
        if S[k]:
            print(k)
