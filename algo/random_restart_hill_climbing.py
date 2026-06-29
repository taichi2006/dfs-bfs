from .common import random_state
from .simple_hill_climbing import simple_hill_climbing


def random_restart_hill_climbing(start, goal, max_restarts=30):
    best_path = None
    best_states = None
    best_len = float("inf")
    for restart in range(max_restarts):
        current_start = random_state(goal) if restart > 0 else start
        path, states = simple_hill_climbing(current_start, goal)
        if path and states and states[-1] == goal and len(path) < best_len:
            best_path, best_states, best_len = path, states, len(path)
    return (best_path, best_states) if best_path else (None, None)
