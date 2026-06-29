from collections import deque

from .common import build_path, neighbors


def bfs(start, goal):
    q = deque([start])
    parent = {start: (None, None)}
    while q:
        cur = q.popleft()
        if cur == goal:
            break
        for nxt, mv in neighbors(cur):
            if nxt not in parent:
                parent[nxt] = (cur, mv)
                q.append(nxt)
    if goal not in parent:
        return None, None
    return build_path(parent, goal)
