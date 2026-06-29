from .common import manhattan, neighbors


def best_hill_climbing(start, goal):
    current = start
    path = []
    states = [current]
    visited = {current}
    while current != goal:
        current_h = manhattan(current, goal)
        best_h = current_h
        best_next = None
        best_move = None
        for nxt, mv in neighbors(current):
            if nxt in visited:
                continue
            h_val = manhattan(nxt, goal)
            if h_val < best_h:
                best_h = h_val
                best_next = nxt
                best_move = mv
        if best_next is None:
            break
        path.append(best_move)
        states.append(best_next)
        visited.add(best_next)
        current = best_next
    return path, states
