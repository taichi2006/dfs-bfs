from collections import deque

from .common import neighbors


def belief_bfs(starts, goal):
    initial_belief = frozenset(starts)
    if all(s == goal for s in initial_belief):
        return [], [initial_belief]
    q = deque([initial_belief])
    parent = {initial_belief: (None, None)}
    while q:
        cur_belief = q.popleft()
        for action in ["U", "D", "L", "R"]:
            next_set = set()
            for s in cur_belief:
                moved = False
                for nxt, mv in neighbors(s):
                    if mv == action:
                        next_set.add(nxt)
                        moved = True
                        break
                if not moved:
                    next_set.add(s)
            next_belief = frozenset(next_set)
            if next_belief in parent:
                continue
            parent[next_belief] = (cur_belief, action)
            if all(state == goal for state in next_belief):
                actions = []
                beliefs = []
                b = next_belief
                while b is not None:
                    beliefs.append(b)
                    prev_b, act = parent[b]
                    if act is not None:
                        actions.append(act)
                    b = prev_b
                return actions[::-1], beliefs[::-1]
            q.append(next_belief)
    return None, None
