from .common import manhattan, neighbors


def forward_checking(start, goal, max_depth=50):
    path = []
    states = [start]
    visited = {start}

    def has_future_domain(state):
        if state == goal:
            return True
        return any(nxt not in visited for nxt, _ in neighbors(state))

    def search(state, depth):
        if state == goal:
            return True
        if depth >= max_depth:
            return False

        domain = []
        for nxt, mv in neighbors(state):
            if nxt in visited:
                continue
            visited.add(nxt)
            ok = has_future_domain(nxt)
            visited.remove(nxt)
            if ok:
                domain.append((manhattan(nxt, goal), nxt, mv))
        domain.sort(key=lambda item: item[0])

        for _, nxt, mv in domain:
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
