from .common import manhattan, neighbors


def simple_hill_climbing(start, goal):
    current = start
    path = []
    states = [current]
    visited = {current}
    while current != goal:
        current_h = manhattan(current, goal)
        found_better = False
        for nxt, mv in neighbors(current):
            if nxt in visited:
                continue
            h_val = manhattan(nxt, goal)
            if h_val < current_h:
                path.append(mv)
                states.append(nxt)
                visited.add(nxt)
                current = nxt
                found_better = True
                break
        if not found_better:
            break
    return path, states
