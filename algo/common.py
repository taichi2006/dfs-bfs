import random


START = (2, 8, 3, 1, 6, 4, 7, 0, 5)
GOAL = (1, 2, 3, 8, 0, 4, 7, 6, 5)


def neighbors(state):
    z = state.index(0)
    r, c = divmod(z, 3)
    for dr, dc, mv in [(-1, 0, "U"), (1, 0, "D"), (0, -1, "L"), (0, 1, "R")]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            nz = nr * 3 + nc
            s = list(state)
            s[z], s[nz] = s[nz], s[z]
            yield tuple(s), mv


def manhattan(state, goal):
    dist = 0
    for v in range(1, 9):
        cur = state.index(v)
        target = goal.index(v)
        r1, c1 = divmod(cur, 3)
        r2, c2 = divmod(target, 3)
        dist += abs(r1 - r2) + abs(c1 - c2)
    return dist


def inv(state):
    a = [x for x in state if x]
    return sum(a[i] > a[j] for i in range(len(a)) for j in range(i + 1, len(a)))


def solvable(a, b):
    return inv(a) % 2 == inv(b) % 2


def random_state(goal):
    while True:
        s = tuple(random.sample(range(9), 9))
        if solvable(s, goal):
            return s


def build_path(parent, goal):
    path, states = [], []
    cur = goal
    while cur:
        states.append(cur)
        p, mv = parent[cur]
        if mv:
            path.append(mv)
        cur = p
    return path[::-1], states[::-1]
