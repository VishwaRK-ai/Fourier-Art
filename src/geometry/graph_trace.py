import numpy as np
from collections import defaultdict, deque

NEIGHBORS = [
    (-1, -1), (-1, 0), (-1, 1),
    ( 0, -1),          ( 0, 1),
    ( 1, -1), ( 1, 0), ( 1, 1),
]

def skeleton_to_graph(skel):
    h, w = skel.shape
    graph = defaultdict(list)

    for y in range(h):
        for x in range(w):
            if skel[y, x]:
                for dy, dx in NEIGHBORS:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and skel[ny, nx]:
                        graph[(x, y)].append((nx, ny))
    return graph


def trace_skeleton(skel):
    graph = skeleton_to_graph(skel)

    if not graph:
        return []

    endpoints = [n for n in graph if len(graph[n]) == 1]
    start = endpoints[0] if endpoints else next(iter(graph))

    visited = set()
    path = []
    stack = deque([start])

    while stack:
        node = stack.pop()
        if node in visited:
            continue

        visited.add(node)
        path.append(node)

        for nb in graph[node]:
            if nb not in visited:
                stack.append(nb)

    return path