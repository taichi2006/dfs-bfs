from .common import build_path, neighbors


def dls(start, goal, limit):
    stack = [(start, 0)]
    parent = {start: (None, None)}
    while stack:
        cur, depth = stack.pop()
        if cur == goal:
            break
        if depth >= limit:
            continue
        for nxt, mv in reversed(list(neighbors(cur))):
            if nxt not in parent:
                parent[nxt] = (cur, mv)
                stack.append((nxt, depth + 1))
    if goal not in parent:
        return None, None
    return build_path(parent, goal)


def ids(start, goal, max_depth=50):
    for limit in range(max_depth + 1):
        path, states = dls(start, goal, limit)
        if path is not None:
            return path, states
    return None, None
