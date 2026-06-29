from collections import deque

from .astar import astar


def revise(domains, xi, xj):
    removed = False
    for x in set(domains[xi]):
        if not any(x != y for y in domains[xj]):
            domains[xi].remove(x)
            removed = True
    return removed


def ac3_consistent(state):
    domains = {i: {state[i]} for i in range(9)}
    arcs = deque((i, j) for i in range(9) for j in range(9) if i != j)
    while arcs:
        xi, xj = arcs.popleft()
        if revise(domains, xi, xj):
            if not domains[xi]:
                return False
            for xk in range(9):
                if xk != xi and xk != xj:
                    arcs.append((xk, xi))
    return True


def ac3(start, goal):
    if not ac3_consistent(start) or not ac3_consistent(goal):
        return None, None
    return astar(start, goal)
