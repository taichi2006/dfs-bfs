import heapq

from .common import build_path, neighbors


def ucs(start, goal):
    pq = []
    heapq.heappush(pq, (0, start))
    parent = {start: (None, None)}
    cost = {start: 0}
    while pq:
        g, cur = heapq.heappop(pq)
        if cur == goal:
            break
        for nxt, mv in neighbors(cur):
            new_cost = g + 1
            if nxt not in cost or new_cost < cost[nxt]:
                cost[nxt] = new_cost
                parent[nxt] = (cur, mv)
                heapq.heappush(pq, (new_cost, nxt))
    if goal not in parent:
        return None, None
    return build_path(parent, goal)
