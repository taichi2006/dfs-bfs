from .common import build_path, neighbors


def dfs(start, goal, limit=35):
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
