import tkinter as tk
from tkinter import messagebox
from collections import deque
import random
import threading
import time
import heapq
import math
from functools import lru_cache

# ================= THEME =================
BG = "#1a1b26"
FRAME = "#24283b"
BTN = "#7aa2f7"
BTN_HOVER = "#9ab8ff"
TEXT = "#ffffff"
EMPTY = "#414868"
TILE = "#c0caf5"
LOG_BG = "#0b1220"
SUCCESS = "#00ff9f"
INFO = "#ffd166"

# ================= STATES =================
START = (2,8,3,1,6,4,7,0,5)
GOAL  = (1,2,3,8,0,4,7,6,5)

# ================= UTILS =================
def neighbors(state):
    z = state.index(0)
    r, c = divmod(z, 3)
    for dr, dc, mv in [(-1,0,'U'),(1,0,'D'),(0,-1,'L'),(0,1,'R')]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            nz = nr * 3 + nc
            s = list(state)
            s[z], s[nz] = s[nz], s[z]
            yield tuple(s), mv

def manhattan(state, goal):
    dist = 0
    for v in range(1, 9):
        cur = state.index(v)
        target = goal.index(v)
        r1, c1 = divmod(cur, 3)
        r2, c2 = divmod(target, 3)
        dist += abs(r1-r2) + abs(c1-c2)
    return dist

def inv(state):
    a = [x for x in state if x]
    return sum(a[i] > a[j] for i in range(len(a)) for j in range(i+1, len(a)))

def solvable(a, b):
    return inv(a) % 2 == inv(b) % 2

def random_state(goal):
    while True:
        s = tuple(random.sample(range(9), 9))
        if solvable(s, goal):
            return s

def build_path(parent, goal):
    path, states = [], []
    cur = goal
    while cur:
        states.append(cur)
        p, mv = parent[cur]
        if mv: path.append(mv)
        cur = p
    return path[::-1], states[::-1]

# ================= CÁC THUẬT TOÁN CŨ =================
def bfs(start, goal):
    q = deque([start])
    parent = {start:(None,None)}
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

def dfs(start, goal, limit=35):
    stack = [(start,0)]
    parent = {start:(None,None)}
    while stack:
        cur, depth = stack.pop()
        if cur == goal:
            break
        if depth >= limit:
            continue
        for nxt, mv in reversed(list(neighbors(cur))):
            if nxt not in parent:
                parent[nxt] = (cur, mv)
                stack.append((nxt, depth+1))
    if goal not in parent:
        return None, None
    return build_path(parent, goal)

def dls(start, goal, limit):
    stack = [(start,0)]
    parent = {start:(None,None)}
    while stack:
        cur, depth = stack.pop()
        if cur == goal:
            break
        if depth >= limit:
            continue
        for nxt, mv in reversed(list(neighbors(cur))):
            if nxt not in parent:
                parent[nxt] = (cur, mv)
                stack.append((nxt, depth+1))
    if goal not in parent:
        return None, None
    return build_path(parent, goal)

def ids(start, goal, max_depth=50):
    for limit in range(max_depth + 1):
        path, states = dls(start, goal, limit)
        if path is not None:
            return path, states
    return None, None

def ucs(start, goal):
    pq = []
    heapq.heappush(pq, (0, start))
    parent = {start:(None,None)}
    cost = {start:0}
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

def greedy(start, goal):
    pq = []
    h = manhattan(start, goal)
    heapq.heappush(pq, (h, start))
    parent = {start:(None,None)}
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

def astar(start, goal):
    pq = []
    g = inv(start)
    h = manhattan(start, goal)
    f = g + h
    heapq.heappush(pq, (f, g, h, start))
    parent = {start:(None,None)}
    visited = set()
    while pq:
        f, g, h, cur = heapq.heappop(pq)
        if cur in visited:
            continue
        visited.add(cur)
        if cur == goal:
            break
        for nxt, mv in neighbors(cur):
            if nxt not in visited:
                gn = inv(nxt)
                hn = manhattan(nxt, goal)
                fn = gn + hn
                if nxt not in parent:
                    parent[nxt] = (cur, mv)
                heapq.heappush(pq, (fn, gn, hn, nxt))
    if goal not in parent:
        return None, None
    return build_path(parent, goal)

def simple_hill_climbing(start, goal):
    current = start
    path = []
    states = [current]
    visited = {current}
    while current != goal:
        current_h = manhattan(current, goal)
        found_better = False
        for nxt, mv in neighbors(current):
            if nxt in visited:
                continue
            h_val = manhattan(nxt, goal)
            if h_val < current_h:
                path.append(mv)
                states.append(nxt)
                visited.add(nxt)
                current = nxt
                found_better = True
                break
        if not found_better:
            break
    return path, states

def best_hill_climbing(start, goal):
    current = start
    path = []
    states = [current]
    visited = {current}
    while current != goal:
        current_h = manhattan(current, goal)
        best_h = current_h
        best_next = None
        best_move = None
        for nxt, mv in neighbors(current):
            if nxt in visited:
                continue
            h_val = manhattan(nxt, goal)
            if h_val < best_h:
                best_h = h_val
                best_next = nxt
                best_move = mv
        if best_next is None:
            break
        path.append(best_move)
        states.append(best_next)
        visited.add(best_next)
        current = best_next
    return path, states

def random_hill_climbing(start, goal):
    current = start
    path = []
    states = [current]
    visited = {current}
    while current != goal:
        current_h = manhattan(current, goal)
        better = []
        for nxt, mv in neighbors(current):
            if nxt in visited:
                continue
            h_val = manhattan(nxt, goal)
            if h_val < current_h:
                better.append((nxt, mv))
        if not better:
            break
        nxt, mv = random.choice(better)
        path.append(mv)
        states.append(nxt)
        visited.add(nxt)
        current = nxt
    return path, states

def random_restart_hill_climbing(start, goal, max_restarts=30):
    best_path = None
    best_states = None
    best_len = float('inf')
    for restart in range(max_restarts):
        current_start = random_state(goal) if restart > 0 else start
        path, states = simple_hill_climbing(current_start, goal)
        if path and states and states[-1] == goal and len(path) < best_len:
            best_path, best_states, best_len = path, states, len(path)
    return (best_path, best_states) if best_path else (None, None)

def local_beam_search_with_path(start, goal, k=3, max_iterations=200):
    beam = [(start, [start], [])]
    for _ in range(k-1):
        beam.append((random_state(goal), [random_state(goal)], []))
    for _ in range(max_iterations):
        candidates = []
        for state, states_list, moves_list in beam:
            if state == goal:
                return moves_list, states_list
            for nxt, mv in neighbors(state):
                if nxt not in states_list:
                    candidates.append((manhattan(nxt, goal), nxt, states_list+[nxt], moves_list+[mv]))
        if not candidates:
            break
        candidates.sort(key=lambda x: x[0])
        beam = [(c[1], c[2], c[3]) for c in candidates[:k]]
    return None, None

def simulated_annealing(start, goal, initial_temp=100.0, alpha=0.95, max_iter=10000):
    current = start
    path = []
    states = [current]
    temp = initial_temp
    for _ in range(max_iter):
        if current == goal:
            break
        nxt, mv = random.choice(list(neighbors(current)))
        delta = manhattan(nxt, goal) - manhattan(current, goal)
        if delta < 0 or random.random() < math.exp(-delta / temp):
            path.append(mv)
            states.append(nxt)
            current = nxt
        temp *= alpha
    return (path, states) if current == goal else (None, None)

def belief_bfs(starts, goal):
    initial_belief = frozenset(starts)
    if all(s == goal for s in initial_belief):
        return [], [initial_belief]
    q = deque([initial_belief])
    parent = {initial_belief: (None, None)}
    while q:
        cur_belief = q.popleft()
        for action in ['U', 'D', 'L', 'R']:
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

# ================= AND-OR GRAPH SEARCH (TỐI ƯU) =================
def and_or_graph_search(initial_belief, goal, max_depth=18):
    """Tìm kiếm AND-OR với giới hạn độ sâu và heuristic để tăng tốc."""
    def next_belief(belief, action):
        nxt = set()
        for s in belief:
            moved = False
            for ns, mv in neighbors(s):
                if mv == action:
                    nxt.add(ns)
                    moved = True
                    break
            if not moved:
                nxt.add(s)
        return frozenset(nxt)

    @lru_cache(maxsize=None)
    def solve(belief, depth):
        if depth > max_depth:
            return False, None, None
        if all(s == goal for s in belief):
            return True, [], [belief]
        
        # Heuristic: sắp xếp action theo tổng Manhattan trung bình (thấp trước)
        actions = ['U', 'D', 'L', 'R']
        action_heuristic = []
        for action in actions:
            nb = next_belief(belief, action)
            avg_h = sum(manhattan(s, goal) for s in nb) / len(nb) if nb else 1e9
            action_heuristic.append((avg_h, action, nb))
        action_heuristic.sort(key=lambda x: x[0])  # ưu tiên avg_h nhỏ
        
        for _, action, nb in action_heuristic:
            ok, sub_actions, sub_beliefs = solve(nb, depth+1)
            if ok:
                return True, [action] + sub_actions, [belief] + sub_beliefs
        return False, None, None

    ok, actions, beliefs = solve(initial_belief, 0)
    if ok:
        return actions, beliefs
    return None, None

# ================= GUI =================
class Puzzle:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle AI Solver")
        self.root.geometry("1400x900")
        self.root.config(bg=BG)
        self.running = False
        self.info_mode = "full"

        tk.Label(root, text="8 PUZZLE AI SOLVER", font=("Arial",28,"bold"),
                 bg=BG, fg="#00d4ff").pack(pady=10)

        main = tk.Frame(root, bg=BG)
        main.pack(fill="both", expand=True, padx=10, pady=5)

        # Khung bên trái (có thanh cuộn)
        left_container = tk.Frame(main, bg=FRAME)
        left_container.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(left_container, bg=FRAME, highlightthickness=0)
        scrollbar = tk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=FRAME)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.start = self.make_grid(scrollable_frame, "START STATE", START)
        tk.Button(scrollable_frame, text="Random Start", font=("Arial",11,"bold"), width=18,
                  bg=BTN, fg="white", command=self.random_start).pack(pady=10)

        self.goal = self.make_grid(scrollable_frame, "GOAL STATE", GOAL)

        bf = tk.Frame(scrollable_frame, bg=FRAME)
        bf.pack(pady=15)

        buttons = [
            ("BFS", self.solve_bfs), ("DFS", self.solve_dfs),
            ("IDS", self.solve_ids), ("UCS", self.solve_ucs),
            ("Greedy", self.solve_greedy), ("A*", self.solve_astar),
            ("Simple Hill", self.solve_simple_hill), ("Best Hill", self.solve_best_hill),
            ("Random Hill", self.solve_random_hill), ("Random Restart", self.solve_restart_hill),
            ("Local Beam (k=3)", self.solve_beam), ("Simulated Annealing", self.solve_sa),
            ("Belief Search", self.solve_belief_bfs),
            ("AND-OR Graph Search", self.solve_and_or)
        ]

        for i, (txt, cmd) in enumerate(buttons):
            b = tk.Button(bf, text=txt, width=16, height=1, font=("Arial",9,"bold"),
                          bg=BTN, fg="white", activebackground=BTN_HOVER,
                          cursor="hand2", command=cmd)
            b.grid(row=i//4, column=i%4, padx=6, pady=6, sticky="nsew")

        reset_btn = tk.Button(scrollable_frame, text="RESET", width=30, height=1,
                              font=("Arial",12,"bold"), bg="#ff5f5f", fg="white",
                              relief="flat", cursor="hand2", command=self.reset)
        reset_btn.pack(pady=20)

        # Khung bên phải
        right = tk.Frame(main, bg=FRAME, bd=2, relief="ridge")
        right.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        title_frame = tk.Frame(right, bg=FRAME)
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="VISUALIZATION", font=("Arial",22,"bold"),
                 bg=FRAME, fg=TEXT).pack()

        board_frame = tk.Frame(right, bg=FRAME)
        board_frame.pack(pady=10)

        self.board1_frame = tk.Frame(board_frame, bg=FRAME, relief="ridge", bd=2)
        self.board1_frame.pack(side="left", padx=10)
        tk.Label(self.board1_frame, text="State 1", font=("Arial",12,"bold"), bg=FRAME, fg=TEXT).pack()
        self.cells1 = []
        board1_grid = tk.Frame(self.board1_frame, bg=FRAME)
        board1_grid.pack()
        for i in range(3):
            row = []
            for j in range(3):
                lbl = tk.Label(board1_grid, width=3, height=1, font=("Arial",28,"bold"),
                               bg=TILE, fg="#111111", relief="ridge", bd=3)
                lbl.grid(row=i, column=j, padx=5, pady=5)
                row.append(lbl)
            self.cells1.append(row)

        self.board2_frame = tk.Frame(board_frame, bg=FRAME, relief="ridge", bd=2)
        self.board2_frame.pack(side="left", padx=10)
        tk.Label(self.board2_frame, text="State 2", font=("Arial",12,"bold"), bg=FRAME, fg=TEXT).pack()
        self.cells2 = []
        board2_grid = tk.Frame(self.board2_frame, bg=FRAME)
        board2_grid.pack()
        for i in range(3):
            row = []
            for j in range(3):
                lbl = tk.Label(board2_grid, width=3, height=1, font=("Arial",28,"bold"),
                               bg=TILE, fg="#111111", relief="ridge", bd=3)
                lbl.grid(row=i, column=j, padx=5, pady=5)
                row.append(lbl)
            self.cells2.append(row)
        self.board2_frame.pack_forget()

        self.status = tk.Label(right, text="READY", font=("Arial",14,"bold"),
                               bg=FRAME, fg=SUCCESS)
        self.status.pack(pady=5)

        self.info = tk.Label(right, text="", font=("Consolas",14,"bold"),
                             bg=FRAME, fg=INFO)
        self.info.pack(pady=5)

        self.log = tk.Text(right, width=50, height=16, font=("Consolas",10),
                           bg=LOG_BG, fg=SUCCESS, relief="flat")
        self.log.pack(padx=15, pady=15, fill="both", expand=True)

        self.draw(START)

    def make_grid(self, parent, title, data):
        tk.Label(parent, text=title, font=("Arial",18,"bold"), bg=FRAME, fg=TEXT).pack(pady=8)
        f = tk.Frame(parent, bg=FRAME)
        f.pack()
        arr = []
        k = 0
        for i in range(3):
            row = []
            for j in range(3):
                e = tk.Entry(f, width=3, font=("Arial",22,"bold"), justify="center",
                             relief="flat", bg="#dbe4ff")
                if data[k]:
                    e.insert(0, str(data[k]))
                e.grid(row=i, column=j, padx=4, pady=4, ipady=5)
                row.append(e)
                k += 1
            arr.append(row)
        return arr

    def read(self, grid):
        try:
            nums = []
            for i in range(3):
                for j in range(3):
                    t = grid[i][j].get().strip()
                    nums.append(0 if t == "" else int(t))
            if sorted(nums) != list(range(9)):
                raise ValueError
            return tuple(nums)
        except:
            messagebox.showerror("Error", "Please enter numbers 0-8 exactly once")
            return None

    def draw(self, state, board=1):
        goal = self.read(self.goal)
        cells = self.cells1 if board == 1 else self.cells2
        for i, v in enumerate(state):
            r, c = divmod(i, 3)
            cells[r][c].config(text="" if v == 0 else str(v),
                               bg=EMPTY if v == 0 else TILE)
        if board == 1 and goal:
            g, h = inv(state), manhattan(state, goal)
            if self.info_mode == "full":
                self.info.config(text=f"g(n)={g} h(n)={h} f(n)={g+h}")
            elif self.info_mode == "only_h":
                self.info.config(text=f"h(n)={h}")
            else:
                self.info.config(text=f"g(n)={g}")
        self.root.update()

    def draw_belief(self, state1, state2):
        self.draw(state1, board=1)
        self.draw(state2, board=2)

    def write(self, txt):
        self.log.insert(tk.END, txt + "\n")
        self.log.see(tk.END)

    def random_start(self):
        if self.running: return
        goal = self.read(self.goal)
        if not goal: return
        s = random_state(goal)
        k = 0
        for i in range(3):
            for j in range(3):
                self.start[i][j].delete(0, tk.END)
                if s[k]: self.start[i][j].insert(0, str(s[k]))
                k += 1
        self.draw(s)

    def animate(self, path, states, algo, belief_pairs=None):
        self.running = True
        self.log.delete(1.0, tk.END)
        self.write("="*45)
        self.write(f"{algo} SOLUTION")
        self.write("="*45)
        if path:
            self.write(f"Steps: {len(path)}")
            self.write(f"Moves: {' '.join(path)}\n")
        goal = self.read(self.goal)

        if algo == "A*":
            self.info_mode = "full"
        elif algo in ["GREEDY","Simple Hill","Best Hill","Random Hill","Random Restart","Local Beam (k=3)","Simulated Annealing"]:
            self.info_mode = "only_h"
        else:
            self.info_mode = "only_g"

        if belief_pairs is not None:
            self.board2_frame.pack(side="left", padx=10)
            for i, (s1, s2) in enumerate(belief_pairs):
                self.draw_belief(s1, s2)
                g1, h1 = inv(s1), manhattan(s1, goal) if goal else 0
                g2, h2 = inv(s2), manhattan(s2, goal) if goal else 0
                if self.info_mode == "full":
                    self.write(f"STEP {i}: State1 g={g1} h={h1} f={g1+h1}")
                    self.write(f"       State2 g={g2} h={h2} f={g2+h2}")
                elif self.info_mode == "only_h":
                    self.write(f"STEP {i}: State1 h={h1}, State2 h={h2}")
                else:
                    self.write(f"STEP {i}: State1 depth={g1}, State2 depth={g2}")
                self.write("State1 matrix:")
                for r in range(0, 9, 3):
                    self.write("   " + str(s1[r:r+3]))
                self.write("State2 matrix:")
                for r in range(0, 9, 3):
                    self.write("   " + str(s2[r:r+3]))
                self.write("-"*40)
                time.sleep(0.35)
            self.board2_frame.pack_forget()
        else:
            self.board2_frame.pack_forget()
            if states:
                for i, s in enumerate(states):
                    self.draw(s)
                    g, h = inv(s), manhattan(s, goal) if goal else 0
                    if self.info_mode == "full":
                        self.write(f"STEP {i}: g={g} h={h} f={g+h}")
                    elif self.info_mode == "only_h":
                        self.write(f"STEP {i}: h={h}")
                    else:
                        self.write(f"STEP {i} (depth={g})")
                    for r in range(0, 9, 3):
                        self.write(str(s[r:r+3]))
                    self.write("-"*40)
                    time.sleep(0.35)
        self.status.config(text=f"{algo} COMPLETED")
        self.running = False

    def solve(self, algo, solver_func):
        if self.running: return
        start = self.read(self.start)
        goal = self.read(self.goal)
        if not start or not goal: return
        if not solvable(start, goal):
            messagebox.showerror("Error", "Unsolvable State")
            return
        self.status.config(text=f"RUNNING {algo}...")
        def run():
            path, states = solver_func(start, goal)
            if path is None:
                messagebox.showinfo("Result", f"{algo} could not find solution")
            else:
                self.animate(path, states, algo)
        threading.Thread(target=run, daemon=True).start()

    def solve_bfs(self): self.solve("BFS", bfs)
    def solve_dfs(self): self.solve("DFS", dfs)
    def solve_ids(self): self.solve("IDS", ids)
    def solve_ucs(self): self.solve("UCS", ucs)
    def solve_greedy(self): self.solve("GREEDY", greedy)
    def solve_astar(self): self.solve("A*", astar)
    def solve_simple_hill(self): self.solve("Simple Hill", simple_hill_climbing)
    def solve_best_hill(self): self.solve("Best Hill", best_hill_climbing)
    def solve_random_hill(self): self.solve("Random Hill", random_hill_climbing)
    def solve_restart_hill(self): self.solve("Random Restart", random_restart_hill_climbing)
    def solve_beam(self): self.solve("Local Beam (k=3)", local_beam_search_with_path)
    def solve_sa(self): self.solve("Simulated Annealing", simulated_annealing)

    def solve_belief_bfs(self):
        if self.running: return
        goal = self.read(self.goal)
        if not goal:
            messagebox.showerror("Error", "Please enter goal state")
            return
        s1 = (1,2,3,8,4,5,7,6,0)
        s2 = (1,2,3,8,4,5,7,0,6)
        self.status.config(text="RUNNING Belief Search...")
        def run():
            actions, beliefs = belief_bfs([s1, s2], goal)
            if actions is None:
                messagebox.showinfo("Result", "No belief-state solution found")
                return
            self.log.delete(1.0, tk.END)
            self.log.insert(tk.END, f"Fixed start states:\n{s1}\n{s2}\n\n")
            self.log.insert(tk.END, "BELIEF STATES\n")
            self.log.insert(tk.END, "=" * 50 + "\n")
            belief_pairs = []
            for b in beliefs:
                lst = list(b)
                if len(lst) >= 2:
                    state_a, state_b = lst[0], lst[1]
                elif len(lst) == 1:
                    state_a = state_b = lst[0]
                else:
                    continue
                belief_pairs.append((state_a, state_b))
                self.log.insert(tk.END, f"Belief (size={len(b)})\n")
                for st in b:
                    self.log.insert(tk.END, str(st) + "\n")
                self.log.insert(tk.END, "-" * 50 + "\n")
            self.animate(actions, None, "Belief Search", belief_pairs=belief_pairs)
        threading.Thread(target=run, daemon=True).start()

    def solve_and_or(self):
        if self.running: return
        goal = self.read(self.goal)
        if not goal:
            messagebox.showerror("Error", "Please enter goal state")
            return
        s1 = (1,2,3,8,4,5,7,6,0)
        s2 = (1,2,3,8,4,5,7,0,6)
        initial_belief = frozenset([s1, s2])
        self.status.config(text="RUNNING AND-OR Graph Search (max_depth=18)...")
        def run():
            actions, beliefs = and_or_graph_search(initial_belief, goal, max_depth=18)
            if actions is None:
                messagebox.showinfo("Result", "AND-OR Graph Search could not find solution within depth limit (18)")
                return
            self.log.delete(1.0, tk.END)
            self.log.insert(tk.END, f"Fixed start states:\n{s1}\n{s2}\n\n")
            self.log.insert(tk.END, "AND-OR SEARCH PLAN\n")
            self.log.insert(tk.END, "=" * 50 + "\n")
            belief_pairs = []
            for b in beliefs:
                lst = list(b)
                if len(lst) >= 2:
                    state_a, state_b = lst[0], lst[1]
                elif len(lst) == 1:
                    state_a = state_b = lst[0]
                else:
                    continue
                belief_pairs.append((state_a, state_b))
                self.log.insert(tk.END, f"Belief state (size={len(b)})\n")
                for st in b:
                    self.log.insert(tk.END, str(st) + "\n")
                self.log.insert(tk.END, "-" * 50 + "\n")
            self.animate(actions, None, "AND-OR Graph Search", belief_pairs=belief_pairs)
        threading.Thread(target=run, daemon=True).start()

    def reset(self):
        if self.running: return
        self.info_mode = "full"
        self.log.delete(1.0, tk.END)
        self.status.config(text="RESET")
        self.draw(START)
        self.board2_frame.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = Puzzle(root)
    root.mainloop()