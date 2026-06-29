from .common import manhattan, neighbors, random_state


def local_beam_search_with_path(start, goal, k=3, max_iterations=200):
    beam = [(start, [start], [])]
    for _ in range(k - 1):
        rs = random_state(goal)
        beam.append((rs, [rs], []))
    for _ in range(max_iterations):
        candidates = []
        for state, states_list, moves_list in beam:
            if state == goal:
                return moves_list, states_list
            for nxt, mv in neighbors(state):
                if nxt not in states_list:
                    candidates.append((manhattan(nxt, goal), nxt, states_list + [nxt], moves_list + [mv]))
        if not candidates:
            break
        candidates.sort(key=lambda x: x[0])
        beam = [(c[1], c[2], c[3]) for c in candidates[:k]]
    return None, None









