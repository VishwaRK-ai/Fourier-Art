import numpy as np
from collections import defaultdict, deque
import math

# utils
def neighbors_8(y, x, h, w):
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w:
                yield ny, nx

def angle(p0, p1):
    return math.atan2(p1[0] - p0[0], p1[1] - p0[1])

# pixel graph
def skeleton_to_graph(skel):
    h, w = skel.shape
    graph = defaultdict(list)
    for y in range(h):
        for x in range(w):
            if skel[y, x] == 0:
                continue
            for ny, nx in neighbors_8(y, x, h, w):
                if skel[ny, nx]:
                    graph[(y, x)].append((ny, nx))
    return graph

# junction resolution
def resolve_junctions(graph):
    new_graph = defaultdict(list)
    for node, nbrs in graph.items():
        if len(nbrs) <= 2:
            new_graph[node].extend(nbrs)
            continue
        angs = sorted((angle(node, n), n) for n in nbrs)
        for i in range(0, len(angs) - 1, 2):
            _, a = angs[i]
            _, b = angs[i + 1]
            new_graph[a].append(b)
            new_graph[b].append(a)
    return new_graph

# Euler traversal
def find_start_node(graph):
    odd = [n for n in graph if len(graph[n]) % 2 == 1]
    return odd[0] if odd else next(iter(graph))

def eulerian_path(graph):
    edges = {u: deque(v) for u, v in graph.items()}
    start = find_start_node(graph)
    stack = [start]
    path = []
    while stack:
        v = stack[-1]
        if edges.get(v):
            u = edges[v].popleft()
            if u in edges and v in edges[u]:
                edges[u].remove(v)
            stack.append(u)
        else:
            path.append(stack.pop())
    return path[::-1]

# stitch all components into one path
def stitch_components(paths):
    if not paths:
        return []

    merged = list(paths[0])
    for path in paths[1:]:
        merged.extend(path)
    return merged

# main function
def trace_skeleton(skel):
    skel = (skel > 0).astype(np.uint8)
    graph = skeleton_to_graph(skel)
    graph = resolve_junctions(graph)

    # find connected components
    visited = set()
    components = []

    for node in list(graph.keys()):
        if node in visited:
            continue
        stack = [node]
        comp = []
        while stack:
            v = stack.pop()
            if v in visited:
                continue
            visited.add(v)
            comp.append(v)
            for u in graph[v]:
                if u not in visited:
                    stack.append(u)
        # Eulerian path for this component
        subgraph = {v: graph[v] for v in comp}
        path = eulerian_path(subgraph)
        if path:
            components.append(path)

    # stitch all components into one
    full_path = stitch_components(components)
    points = np.array([[x, y] for (y, x) in full_path], dtype=np.float32)
    return points