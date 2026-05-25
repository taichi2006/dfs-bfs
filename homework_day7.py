import tkinter as tk
from tkinter import messagebox
from collections import deque
import random
import threading
import time
import heapq

# ================= COLORS =================
BG = "#1a1b26"
FRAME = "#24283b"
BTN = "#7aa2f7"
TEXT = "#ffffff"
EMPTY = "#414868"
TILE = "#c0caf5"

# ================= STATES =================
START = (2,8,3,1,6,4,7,0,5)
GOAL  = (1,2,3,8,0,4,7,6,5)

# ================= UTILS =================
def neighbors(state):

    z = state.index(0)

    r, c = divmod(z, 3)

    for dr, dc, mv in [
        (-1,0,'U'),
        (1,0,'D'),
        (0,-1,'L'),
        (0,1,'R')
    ]:

        nr, nc = r + dr, c + dc

        if 0 <= nr < 3 and 0 <= nc < 3:

            nz = nr * 3 + nc

            s = list(state)

            s[z], s[nz] = s[nz], s[z]

            yield tuple(s), mv

def inv(state):

    a = [x for x in state if x]

    return sum(
        a[i] > a[j]
        for i in range(len(a))
        for j in range(i+1, len(a))
    )

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

        self.root.title("8 Puzzle Visual Solver")

        self.root.geometry("1100x720")

        self.root.config(bg=BG)

        self.running = False

        tk.Label(
            root,
            text="8 PUZZLE VISUAL SOLVER",
            font=("Arial",28,"bold"),
            bg=BG,
            fg="#00d4ff"
        ).pack(pady=15)

        main = tk.Frame(root, bg=FRAME)

        main.pack(fill="both", expand=True, padx=20, pady=10)

        # ============ LEFT ============
        left = tk.Frame(main, bg=FRAME)

        left.pack(side="left", padx=30)

        self.start = self.make_grid(
            left,
            "START STATE",
            START
        )

        tk.Button(
            left,
            text="Random Start",
            bg=BTN,
            fg="white",
            width=18,
            command=self.random_start
        ).pack(pady=15)

        self.goal = self.make_grid(
            left,
            "GOAL STATE",
            GOAL
        )

        bf = tk.Frame(left, bg=FRAME)

        bf.pack(pady=20)

        buttons = [
            ("Solve BFS", self.solve_bfs),
            ("Solve DFS", self.solve_dfs),
            ("Solve IDS", self.solve_ids),
            ("Solve UCS", self.solve_ucs),
            ("Reset", self.reset)
        ]

        for i, (txt, cmd) in enumerate(buttons):

            tk.Button(
                bf,
                text=txt,
                bg=BTN,
                fg="white",
                width=12,
                command=cmd
            ).grid(
                row=i//2,
                column=i%2,
                padx=8,
                pady=8
            )

        # ============ RIGHT ============
        right = tk.Frame(main, bg=FRAME)

        right.pack(side="right", padx=30)

        tk.Label(
            right,
            text="VISUALIZATION",
            font=("Arial",22,"bold"),
            bg=FRAME,
            fg=TEXT
        ).pack(pady=10)

        board = tk.Frame(right, bg=FRAME)

        board.pack()

        self.cells = []

        for i in range(3):

            row = []

            for j in range(3):

                lbl = tk.Label(
                    board,
                    width=4,
                    height=2,
                    font=("Arial",30,"bold"),
                    bg=TILE
                )

                lbl.grid(
                    row=i,
                    column=j,
                    padx=6,
                    pady=6
                )

                row.append(lbl)

            self.cells.append(row)

        self.status = tk.Label(
            right,
            text="READY",
            font=("Arial",14,"bold"),
            bg=FRAME,
            fg="#00ff9f"
        )

        self.status.pack(pady=12)

        self.log = tk.Text(
            right,
            width=42,
            height=18,
            font=("Consolas",11),
            bg="#0b1220",
            fg="#00ff9f"
        )

        self.log.pack()

        self.draw(START)

    # ================= GRID =================
    def make_grid(self, parent, title, data):

        tk.Label(
            parent,
            text=title,
            font=("Arial",18,"bold"),
            bg=FRAME,
            fg=TEXT
        ).pack(pady=10)

        f = tk.Frame(parent, bg=FRAME)

        f.pack()

        arr = []

        k = 0

        for i in range(3):

            row = []

            for j in range(3):

                e = tk.Entry(
                    f,
                    width=3,
                    font=("Arial",28,"bold"),
                    justify="center"
                )

                if data[k]:
                    e.insert(0, str(data[k]))

                e.grid(
                    row=i,
                    column=j,
                    padx=5,
                    pady=5
                )

                row.append(e)

                k += 1

            arr.append(row)

        return arr

    # ================= READ =================
    def read(self, grid):

        try:

            nums = []

            for i in range(3):
                for j in range(3):

                    t = grid[i][j].get().strip()

                    nums.append(
                        0 if t == "" else int(t)
                    )

            if sorted(nums) != list(range(9)):
                raise ValueError

            return tuple(nums)

        except:

            messagebox.showerror(
                "Error",
                "Nhap du so 0-8"
            )

            return None

    # ================= DRAW =================
    def draw(self, state):

        for i, v in enumerate(state):

            r, c = divmod(i, 3)

            self.cells[r][c].config(
                text="" if v == 0 else str(v),
                bg=EMPTY if v == 0 else TILE
            )

        self.root.update()

    # ================= LOG =================
    def write(self, txt):

        self.log.insert(tk.END, txt + "\n")

        self.log.see(tk.END)

    # ================= RANDOM =================
    def random_start(self):

        if self.running:
            return

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

    # ================= ANIMATE =================
    def animate(self, path, states, algo):

        self.running = True

        self.log.delete(1.0, tk.END)

        self.write(f"{algo} SOLUTION")
        self.write(f"Steps : {len(path)}")
        self.write(f"Moves : {' '.join(path)}")
        self.write("")

        for i, s in enumerate(states):

            self.draw(s)

            self.write(f"Step {i}")

            for r in range(0, 9, 3):
                self.write(str(s[r:r+3]))

            self.write("")

            time.sleep(0.4)

        self.status.config(
            text=f"{algo} COMPLETED"
        )

        self.running = False

    # ================= SOLVE =================
    def solve(self, algo):

        if self.running:
            return

        start = self.read(self.start)

        goal = self.read(self.goal)

        if not start or not goal:
            return

        if not solvable(start, goal):

            messagebox.showerror(
                "Error",
                "Unsolvable"
            )

            return

        self.status.config(
            text=f"RUNNING {algo}..."
        )

        def run():

            if algo == "BFS":

                path, states = bfs(start, goal)

            elif algo == "DFS":

                path, states = dfs(start, goal)

            elif algo == "IDS":

                path, states = ids(start, goal)

            else:

                path, states = ucs(start, goal)

            if path is None:

                messagebox.showinfo(
                    "Result",
                    "No Solution"
                )

                return

            self.animate(path, states, algo)

        threading.Thread(
            target=run,
            daemon=True
        ).start()

    def solve_bfs(self):
        self.solve("BFS")

    def solve_dfs(self):
        self.solve("DFS")

    def solve_ids(self):
        self.solve("IDS")

    def solve_ucs(self):
        self.solve("UCS")

    # ================= RESET =================
    def reset(self):

        if self.running:
            return

        self.log.delete(1.0, tk.END)

        self.status.config(text="RESET")

        self.draw(START)

# ================= MAIN =================
root = tk.Tk()

Puzzle(root)

root.mainloop()