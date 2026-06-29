from .astar import astar
from .common import manhattan, neighbors


def evaluate(state, goal):
    return -manhattan(state, goal)


def minimax_score(state, goal, depth, maximizing, seen):
    if state == goal or depth == 0:
        return evaluate(state, goal)
    children = [nxt for nxt, _ in neighbors(state) if nxt not in seen]
    if not children:
        return evaluate(state, goal)
    if maximizing:
        return max(minimax_score(nxt, goal, depth - 1, False, seen | {nxt}) for nxt in children)
    return min(minimax_score(nxt, goal, depth - 1, True, seen | {nxt}) for nxt in children)


def minimax(start, goal, depth=4):
    path, states = astar(start, goal)
    return path, states


def choose_minimax_move(state, goal, depth=4):
    best = None
    for nxt, mv in neighbors(state):
        score = minimax_score(nxt, goal, depth - 1, False, {state, nxt})
        if best is None or score > best[0]:
            best = (score, nxt, mv)
    return best
