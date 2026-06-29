import heapq

from .common import build_path, manhattan, neighbors


def astar(start, goal):
    g = 0
    h = manhattan(start, goal)
    f = g + h
    pq = [(f, g, start)]
    parent = {start: (None, None)}
    visited = set()
    while pq:
        f, g, cur = heapq.heappop(pq)
        if cur in visited:
            continue
        visited.add(cur)
        if cur == goal:
            break
        for nxt, mv in neighbors(cur):
            if nxt not in visited:
                new_g = g + 1
                new_h = manhattan(nxt, goal)
                new_f = new_g + new_h
                if nxt not in parent:
                    parent[nxt] = (cur, mv)
                heapq.heappush(pq, (new_f, new_g, nxt))
    if goal not in parent:
        return None, None
    return build_path(parent, goal)
