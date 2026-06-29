import heapq

from .common import build_path, manhattan, neighbors


def greedy(start, goal):
    pq = []
    h = manhattan(start, goal)
    heapq.heappush(pq, (h, start))
    parent = {start: (None, None)}
    visited = set()
    while pq:
        h, cur = heapq.heappop(pq)
        if cur in visited:
            continue
        visited.add(cur)
        if cur == goal:
            break
        for nxt, mv in neighbors(cur):
            if nxt not in visited:
                parent[nxt] = (cur, mv)
                hn = manhattan(nxt, goal)
                heapq.heappush(pq, (hn, nxt))
    if goal not in parent:
        return None, None
    return build_path(parent, goal)
