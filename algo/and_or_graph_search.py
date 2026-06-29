import heapq

from .common import build_path, manhattan, neighbors


def and_or_graph_search(start, goal):
    def heuristic(state):
        return manhattan(state, goal) + sum(1 for i in range(9) if state[i] != goal[i] and state[i] != 0)

    g = 0
    h = heuristic(start)
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
                new_h = heuristic(nxt)
                new_f = new_g + new_h
                if nxt not in parent:
                    parent[nxt] = (cur, mv)
                heapq.heappush(pq, (new_f, new_g, nxt))
    if goal not in parent:
        return None, None
    return build_path(parent, goal)
