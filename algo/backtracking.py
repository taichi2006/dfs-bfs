from .common import neighbors


def backtracking(start, goal, max_depth=50):
    path = []
    states = [start]
    visited = {start}

    def search(state, depth):
        if state == goal:
            return True
        if depth >= max_depth:
            return False
        for nxt, mv in neighbors(state):
            if nxt in visited:
                continue
            visited.add(nxt)
            path.append(mv)
            states.append(nxt)
            if search(nxt, depth + 1):
                return True
            states.pop()
            path.pop()
            visited.remove(nxt)
        return False

    if search(start, 0):
        return path, states
    return None, None
