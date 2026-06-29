from .common import manhattan, neighbors


def ida_star(start, goal):
    def search(path, g, bound):
        node = path[-1]
        f = g + manhattan(node, goal)
        if f > bound:
            return f, None
        if node == goal:
            return True, path
        next_bound = float("inf")
        for nxt, mv in neighbors(node):
            if nxt not in path:
                path.append(nxt)
                result, solution = search(path, g + 1, bound)
                if result is True:
                    return True, solution
                if result < next_bound:
                    next_bound = result
                path.pop()
        return next_bound, None

    bound = manhattan(start, goal)
    path = [start]
    while True:
        result, solution = search(path, 0, bound)
        if result is True:
            moves = []
            states = solution
            for i in range(len(states) - 1):
                for ns, mv in neighbors(states[i]):
                    if ns == states[i + 1]:
                        moves.append(mv)
                        break
            return moves, states
        if result == float("inf"):
            return None, None
        bound = result
