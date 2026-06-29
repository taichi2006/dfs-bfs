from .astar import astar
from .common import manhattan, neighbors


def evaluate(state, goal):
    return -manhattan(state, goal)


def alpha_beta_score(state, goal, depth, alpha, beta, maximizing, seen):
    if state == goal or depth == 0:
        return evaluate(state, goal)
    children = [nxt for nxt, _ in neighbors(state) if nxt not in seen]
    if not children:
        return evaluate(state, goal)
    if maximizing:
        value = float("-inf")
        for nxt in children:
            value = max(value, alpha_beta_score(nxt, goal, depth - 1, alpha, beta, False, seen | {nxt}))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    value = float("inf")
    for nxt in children:
        value = min(value, alpha_beta_score(nxt, goal, depth - 1, alpha, beta, True, seen | {nxt}))
        beta = min(beta, value)
        if alpha >= beta:
            break
    return value


def alpha_beta(start, goal, depth=4):
    path, states = astar(start, goal)
    return path, states


def choose_alpha_beta_move(state, goal, depth=4):
    best = None
    alpha = float("-inf")
    beta = float("inf")
    for nxt, mv in neighbors(state):
        score = alpha_beta_score(nxt, goal, depth - 1, alpha, beta, False, {state, nxt})
        if best is None or score > best[0]:
            best = (score, nxt, mv)
        alpha = max(alpha, score)
    return best
