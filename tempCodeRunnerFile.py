import tkinter as tk
from tkinter import messagebox
from collections import deque
import random
import threading
import time
import heapq

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

# ================= BFS =================
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

# ================= DFS =================
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

# ================= DLS =================
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

# ================= IDS =================
def ids(start, goal, max_depth=50):
    for limit in range(max_depth + 1):
        path, states = dls(start, goal, limit)
        if path is not None:
            return path, states
    return None, None

# ================= UCS =================
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

# ================= GREEDY =================
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

# ================= A* =================
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

# ================= SIMPLE HILL CLIMBING =================
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

# ================= BEST HILL CLIMBING =================
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

# ================= RANDOM CHOICE HILL CLIMBING =================
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

# ================= RANDOM RESTART HILL CLIMBING =================
def random_restart_hill_climbing(start, goal, max_restarts=30, max_steps=100):
    best_path = None
    best_states = None
    best_len = float('inf')
    
    # Dùng start ban đầu làm lần đầu
    for restart in range(max_restarts):
        if restart == 0:
            current_start = start
        else:
            # Tạo trạng thái ngẫu nhiên có thể giải được
            current_start = random_state(goal)
        
        # Chạy simple hill climbing (hoặc best) từ start này
        path, states = simple_hill_climbing(current_start, goal)
        
        if path is None:
            continue
        
        if states and states[-1] == goal:
            # Tìm thấy lời giải
            if len(path) < best_len:
                best_path = path
                best_states = states
                best_len = len(path)
            # Nếu đã tìm được lời giải ngắn, có thể dừng sớm (tuỳ)
            # break
    
    if best_path is None:
        return None, None
    return best_path, best_states

# ================= LOCAL BEAM SEARCH =================
def local_beam_search(start, goal, k=3, max_iterations=200):
    # Khởi tạo k trạng thái ngẫu nhiên (bao gồm start)
    states = [start]
    for _ in range(k-1):
        s = random_state(goal)
        states.append(s)
    
    # Dùng set để lưu các trạng thái đã xét (tránh lặp vô hạn trong cùng một beam)
    visited_global = set()
    
    for iteration in range(max_iterations):
        # Sinh tất cả neighbor của các trạng thái hiện tại
        candidates = []
        for s in states:
            if s == goal:
                # Nếu đã có goal trong beam, xây dựng đường đi từ start đến goal
                # Cần reconstruct path. Ta sẽ tìm đường từ start đến goal qua BFS? 
                # Để đơn giản, ta sẽ chạy BFS từ start đến goal ngay khi phát hiện.
                # Tuy nhiên beam search không lưu parent, nên ta sẽ dùng BFS để tìm path thực tế.
                # Giải pháp: lưu parent trong quá trình sinh? Phức tạp. Thay vào đó, khi tìm thấy goal,
                # ta sẽ tìm đường bằng BFS từ start thực sự.
                pass
            for nxt, mv in neighbors(s):
                if nxt not in visited_global:
                    visited_global.add(nxt)
                    h_val = manhattan(nxt, goal)
                    candidates.append((h_val, nxt, mv, s))  # lưu thêm s và mv để trace
        
        if not candidates:
            break
        
        # Chọn k candidate có h(n) nhỏ nhất (giữ lại các trạng thái tốt nhất)
        candidates.sort(key=lambda x: x[0])
        best_candidates = candidates[:k]
        
        # Cập nhật beam mới
        new_states = []
        parent_info = {}  # để reconstruct path: nxt -> (prev, move)
        for h_val, nxt, mv, prev in best_candidates:
            new_states.append(nxt)
            parent_info[nxt] = (prev, mv)
        
        states = new_states
        
        # Kiểm tra nếu goal có trong beam
        if goal in states:
            # Tìm đường đi từ start đến goal bằng cách dùng parent_info (chỉ lưu được các bước trong beam, không đủ)
            # Vì beam không lưu toàn bộ lịch sử, ta sẽ dùng BFS từ start để tìm path thực tế.
            # Phương án đơn giản: dùng BFS từ start gốc đến goal (vì bài toán nhỏ, BFS nhanh)
            path, states_path = bfs(start, goal)
            return path, states_path
    
    # Nếu không tìm thấy goal, trả về None
    # Hoặc có thể trả về đường đi từ start đến trạng thái tốt nhất? Không cần.
    return None, None

# Cải tiến local beam search có lưu parent để tìm đường đi từ start đến goal
def local_beam_search_with_path(start, goal, k=3, max_iterations=200):
    # Khởi tạo beam: mỗi phần tử là (state, path_so_far, visited_set)
    # Để tránh lặp trong mỗi nhánh, ta dùng path là list các state và moves
    beam = [(start, [start], [])]  # (state, states_list, moves_list)
    for _ in range(k-1):
        s = random_state(goal)
        beam.append((s, [s], []))
    
    for iteration in range(max_iterations):
        candidates = []
        for state, states_list, moves_list in beam:
            if state == goal:
                return moves_list, states_list
            for nxt, mv in neighbors(state):
                if nxt not in states_list:  # tránh lặp trong cùng nhánh
                    new_states = states_list + [nxt]
                    new_moves = moves_list + [mv]
                    h_val = manhattan(nxt, goal)
                    candidates.append((h_val, nxt, new_states, new_moves))
        if not candidates:
            break
        candidates.sort(key=lambda x: x[0])
        beam = [(c[1], c[2], c[3]) for c in candidates[:k]]
    
    # Nếu không tìm thấy goal, trả về None
    return None, None

# ================= BUILD PATH =================
def build_path(parent, goal):
    path = []
    states = []
    cur = goal
    while cur:
        states.append(cur)
        p, mv = parent[cur]
        if mv:
            path.append(mv)
        cur = p
    return path[::-1], states[::-1]

# ================= GUI =================
class Puzzle:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle AI Solver")
        self.root.geometry("1400x900")
        self.root.config(bg=BG)
        self.running = False
        self.info_mode = "full"

        # Title
        tk.Label(root, text="8 PUZZLE AI SOLVER", font=("Arial",28,"bold"),
                 bg=BG, fg="#00d4ff").pack(pady=10)

        main = tk.Frame(root, bg=BG)
        main.pack(fill="both", expand=True, padx=10, pady=5)

        # LEFT PANEL with Scrollbar
        left_container = tk.Frame(main, bg=FRAME)
        left_container.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(left_container, bg=FRAME, highlightthickness=0)
        scrollbar = tk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=FRAME)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.start = self.make_grid(scrollable_frame, "START STATE", START)
        tk.Button(scrollable_frame, text="Random Start", font=("Arial",11,"bold"), width=18, height=1,
                  bg=BTN, fg="white", activebackground=BTN_HOVER, relief="flat",
                  command=self.random_start).pack(pady=10)

        self.goal = self.make_grid(scrollable_frame, "GOAL STATE", GOAL)

        # BUTTON AREA - Thêm hai nút mới
        bf = tk.Frame(scrollable_frame, bg=FRAME)
        bf.pack(pady=15)

        buttons = [
            ("BFS", self.solve_bfs),
            ("DFS", self.solve_dfs),
            ("IDS", self.solve_ids),
            ("UCS", self.solve_ucs),
            ("Greedy", self.solve_greedy),
            ("A*", self.solve_astar),
            ("Simple Hill", self.solve_simple_hill),
            ("Best Hill", self.solve_best_hill),
            ("Random Hill", self.solve_random_hill),
            ("Random Restart", self.solve_restart_hill),
            ("Local Beam (k=3)", self.solve_beam)
        ]

        # Sắp xếp thành 4 cột
        for i, (txt, cmd) in enumerate(buttons):
            b = tk.Button(bf, text=txt, width=14, height=1, font=("Arial",9,"bold"),
                          bg=BTN, fg="white", activebackground=BTN_HOVER, relief="flat",
                          cursor="hand2", command=cmd)
            b.grid(row=i//4, column=i%4, padx=6, pady=6, sticky="nsew")

        reset_btn = tk.Button(bf, text="RESET", width=60, height=1, font=("Arial",10,"bold"),
                              bg="#ff5f5f", fg="white", relief="flat", cursor="hand2",
                              command=self.reset)
        reset_btn.grid(row=3, column=0, columnspan=4, padx=6, pady=10, sticky="nsew")

        # RIGHT PANEL
        right = tk.Frame(main, bg=FRAME, bd=2, relief="ridge")
        right.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        tk.Label(right, text="VISUALIZATION", font=("Arial",22,"bold"),
                 bg=FRAME, fg=TEXT).pack(pady=10)

        board = tk.Frame(right, bg=FRAME)
        board.pack(pady=10)
        self.cells = []
        for i in range(3):
            row = []
            for j in range(3):
                lbl = tk.Label(board, width=3, height=1, font=("Arial",28,"bold"),
                               bg=TILE, fg="#111111", relief="ridge", bd=3)
                lbl.grid(row=i, column=j, padx=5, pady=5)
                row.append(lbl)
            self.cells.append(row)

        self.status = tk.Label(right, text="READY", font=("Arial",14,"bold"),
                               bg=FRAME, fg=SUCCESS)
        self.status.pack(pady=5)

        self.info = tk.Label(right, text="", font=("Consolas",14,"bold"),
                             bg=FRAME, fg=INFO)
        self.info.pack(pady=5)

        self.log = tk.Text(right, width=50, height=16, font=("Consolas",10),
                           bg=LOG_BG, fg=SUCCESS, relief="flat", insertbackground="white")
        self.log.pack(padx=15, pady=15, fill="both", expand=True)

        self.draw(START)

    def make_grid(self, parent, title, data):
        tk.Label(parent, text=title, font=("Arial",18,"bold"),
                 bg=FRAME, fg=TEXT).pack(pady=8)
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

    def draw(self, state):
        goal = self.read(self.goal)
        for i, v in enumerate(state):
            r, c = divmod(i, 3)
            self.cells[r][c].config(text="" if v == 0 else str(v),
                                    bg=EMPTY if v == 0 else TILE)

        if goal is None:
            return
        g = inv(state)
        h = manhattan(state, goal)
        if self.info_mode == "full":
            f = g + h
            self.info.config(text=f"g(n) = {g}     h(n) = {h}     f(n) = {f}")
        elif self.info_mode == "only_h":
            self.info.config(text=f"h(n) = {h}")
        else:
            self.info.config(text=f"g(n) = {g}     (no heuristic)")
        self.root.update()

    def write(self, txt):
        self.log.insert(tk.END, txt + "\n")
        self.log.see(tk.END)

    def random_start(self):
        if self.running:
            return
        self.info_mode = "full"
        g = self.read(self.goal)
        if not g:
            return
        s = random_state(g)
        k = 0
        for i in range(3):
            for j in range(3):
                self.start[i][j].delete(0, tk.END)
                if s[k]:
                    self.start[i][j].insert(0, str(s[k]))
                k += 1
        self.draw(s)

    def animate(self, path, states, algo):
        self.running = True
        self.log.delete(1.0, tk.END)
        self.write("="*45)
        self.write(f"{algo} SOLUTION")
        self.write("="*45)
        self.write(f"Steps : {len(path)}")
        self.write(f"Moves : {' '.join(path)}")
        self.write("")
        goal = self.read(self.goal)

        if algo == "A*":
            self.info_mode = "full"
        elif algo in ["GREEDY", "Simple Hill", "Best Hill", "Random Hill", "Random Restart", "Local Beam (k=3)"]:
            self.info_mode = "only_h"
        else:
            self.info_mode = "only_g"

        for i, s in enumerate(states):
            self.draw(s)
            g = inv(s)
            h = manhattan(s, goal) if goal else 0
            if self.info_mode == "full":
                f = g + h
                self.write(f"STEP {i}")
                self.write(f"g(n) = {g}     h(n) = {h}     f(n) = {f}")
            elif self.info_mode == "only_h":
                self.write(f"STEP {i}")
                self.write(f"h(n) = {h}")
            else:
                self.write(f"STEP {i} (depth = {g})")
            for r in range(0, 9, 3):
                self.write(str(s[r:r+3]))
            self.write("-"*40)
            time.sleep(0.35)
        self.status.config(text=f"{algo} COMPLETED")
        self.running = False

    def solve(self, algo, solver_func):
        if self.running:
            return
        start = self.read(self.start)
        goal = self.read(self.goal)
        if not start or not goal:
            return
        if not solvable(start, goal):
            messagebox.showerror("Error", "Unsolvable State")
            return
        self.status.config(text=f"RUNNING {algo}...")
        def run():
            path, states = solver_func(start, goal)
            if path is None:
                messagebox.showinfo("Result", f"{algo} could not find solution")
                return
            self.animate(path, states, algo)
        threading.Thread(target=run, daemon=True).start()

    def solve_bfs(self):
        self.solve("BFS", bfs)
    def solve_dfs(self):
        self.solve("DFS", dfs)
    def solve_ids(self):
        self.solve("IDS", ids)
    def solve_ucs(self):
        self.solve("UCS", ucs)
    def solve_greedy(self):
        self.solve("GREEDY", greedy)
    def solve_astar(self):
        self.solve("A*", astar)
    def solve_simple_hill(self):
        self.solve("Simple Hill", simple_hill_climbing)
    def solve_best_hill(self):
        self.solve("Best Hill", best_hill_climbing)
    def solve_random_hill(self):
        self.solve("Random Hill", random_hill_climbing)
    def solve_restart_hill(self):
        self.solve("Random Restart", random_restart_hill_climbing)
    def solve_beam(self):
        self.solve("Local Beam (k=3)", local_beam_search_with_path)

    def reset(self):
        if self.running:
            return
        self.info_mode = "full"
        self.log.delete(1.0, tk.END)
        self.status.config(text="RESET")
        self.draw(START)

if __name__ == "__main__":
    root = tk.Tk()
    app = Puzzle(root)
    root.mainloop()