import random

from .common import manhattan, neighbors


def random_hill_climbing(start, goal):
    current = start
    path = []
    states = [current]
    visited = {current}
    while current != goal:
        current_h = manhattan(current, goal)
        better = []
        for nxt, mv in neighbors(current):
            if nxt in visited:
                continue
            h_val = manhattan(nxt, goal)
            if h_val < current_h:
                better.append((nxt, mv))
        if not better:
            break
        nxt, mv = random.choice(better)
        path.append(mv)
        states.append(nxt)
        visited.add(nxt)
        current = nxt
    return path, states
