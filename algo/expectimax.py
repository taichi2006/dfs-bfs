from .astar import astar
from .common import manhattan, neighbors


def evaluate(state, goal):
    return -manhattan(state, goal)


def expectimax_score(state, goal, depth, maximizing, seen):
    if state == goal or depth == 0:
        return evaluate(state, goal)
    children = [nxt for nxt, _ in neighbors(state) if nxt not in seen]
    if not children:
        return evaluate(state, goal)
    if maximizing:
        return max(expectimax_score(nxt, goal, depth - 1, False, seen | {nxt}) for nxt in children)
    return sum(expectimax_score(nxt, goal, depth - 1, True, seen | {nxt}) for nxt in children) / len(children)


def expectimax(start, goal, depth=4):
    path, states = astar(start, goal)
    return path, states


def choose_expectimax_move(state, goal, depth=4):
    best = None
    for nxt, mv in neighbors(state):
        score = expectimax_score(nxt, goal, depth - 1, False, {state, nxt})
        if best is None or score > best[0]:
            best = (score, nxt, mv)
    return best
