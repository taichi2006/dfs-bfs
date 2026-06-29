import math
import random

from .common import manhattan, neighbors


def simulated_annealing(start, goal, initial_temp=80.0, alpha=0.997, max_iter=4000, restarts=80):
    """Simulated Annealing with restarts and an animation trace."""
    directions = {"U": "len", "D": "xuong", "L": "trai", "R": "phai"}
    best_overall_h = manhattan(start, goal)
    best_overall_states = [start]
    best_overall_path = []
    best_overall_trace = [{
        "step": 0, "restart": 0, "iteration": 0, "move": "START",
        "temp": initial_temp, "current_h": best_overall_h, "next_h": best_overall_h,
        "delta": 0, "probability": 1.0, "accepted": True,
        "reason": "Trang thai bat dau", "rejected": 0
    }]

    for restart in range(restarts):
        current = start
        current_h = manhattan(current, goal)
        path = []
        states = [current]
        trace = [{
            "step": 0, "restart": restart + 1, "iteration": 0, "move": "START",
            "temp": initial_temp, "current_h": current_h, "next_h": current_h,
            "delta": 0, "probability": 1.0, "accepted": True,
            "reason": "Trang thai bat dau", "rejected": 0
        }]
        temp = initial_temp
        rejected = 0

        for iteration in range(1, max_iter + 1):
            if current == goal:
                simulated_annealing.last_trace = trace
                return path, states

            choices = list(neighbors(current))
            random.shuffle(choices)
            choices.sort(key=lambda item: manhattan(item[0], goal))
            if random.random() < 0.70:
                nxt, mv = choices[0]
            else:
                nxt, mv = random.choice(choices)

            next_h = manhattan(nxt, goal)
            delta = next_h - current_h
            probability = 1.0 if delta <= 0 else math.exp(-delta / max(temp, 1e-9))
            accepted = delta <= 0 or random.random() < probability

            if accepted:
                reason = "Tot hon/khong te hon" if delta <= 0 else "Chap nhan do xac suat nhiet do"
                path.append(mv)
                states.append(nxt)
                trace.append({
                    "step": len(path), "restart": restart + 1, "iteration": iteration,
                    "move": mv, "move_text": directions[mv], "temp": temp,
                    "current_h": current_h, "next_h": next_h, "delta": delta,
                    "probability": probability, "accepted": True,
                    "reason": reason, "rejected": rejected
                })
                current = nxt
                current_h = next_h
                rejected = 0

                if current_h < best_overall_h:
                    best_overall_h = current_h
                    best_overall_states = states[:]
                    best_overall_path = path[:]
                    best_overall_trace = trace[:]

                if current == goal:
                    simulated_annealing.last_trace = trace
                    return path, states
            else:
                rejected += 1

            temp *= alpha
            if temp < 0.01:
                break

    simulated_annealing.last_trace = best_overall_trace
    return (best_overall_path, best_overall_states) if best_overall_path else (None, None)
