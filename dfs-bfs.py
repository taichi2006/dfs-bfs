import tkinter as tk
from tkinter import messagebox
from collections import deque
import random
import threading
import time

# =====================================================
# COLORS
# =====================================================
BG = "#1a1b26"
FRAME = "#24283b"
BTN = "#7aa2f7"
TEXT = "#ffffff"
EMPTY = "#414868"
TILE = "#c0caf5"

# =====================================================
# DEFAULT GOAL
# =====================================================
DEFAULT_GOAL = (
    1, 2, 3,
    8, 0, 4,
    7, 6, 5
)

# =====================================================
# GET NEIGHBORS
# =====================================================
def get_neighbors(state):

    neighbors = []

    zero = state.index(0)

    row = zero // 3
    col = zero % 3

    directions = [
        (-1, 0, 'U'),
        (1, 0, 'D'),
        (0, -1, 'L'),
        (0, 1, 'R')
    ]

    for dr, dc, move in directions:

        nr = row + dr
        nc = col + dc

        if 0 <= nr < 3 and 0 <= nc < 3:

            nxt = nr * 3 + nc

            temp = list(state)

            temp[zero], temp[nxt] = \
                temp[nxt], temp[zero]

            neighbors.append(
                (tuple(temp), move)
            )

    return neighbors

# =====================================================
# INVERSION COUNT
# =====================================================
def inversion_count(state):

    arr = [x for x in state if x != 0]

    inv = 0

    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):

            if arr[i] > arr[j]:
                inv += 1

    return inv

# =====================================================
# CHECK SOLVABLE
# =====================================================
def is_solvable(start, goal):

    return (
        inversion_count(start) % 2
        ==
        inversion_count(goal) % 2
    )

# =====================================================
# RANDOM STATE
# =====================================================
def generate_random_state(goal):

    nums = list(range(9))

    while True:

        random.shuffle(nums)

        state = tuple(nums)

        if is_solvable(state, goal):
            return state

# =====================================================
# BFS
# =====================================================
def bfs(start, goal):

    queue = deque([start])

    visited = set([start])

    parent = {}

    move_taken = {}

    while queue:

        state = queue.popleft()

        if state == goal:

            path = []
            states = []

            cur = goal

            while cur != start:

                states.append(cur)

                path.append(
                    move_taken[cur]
                )

                cur = parent[cur]

            states.append(start)

            states.reverse()
            path.reverse()

            return path, states

        for nxt, move in get_neighbors(state):

            if nxt not in visited:

                visited.add(nxt)

                parent[nxt] = state

                move_taken[nxt] = move

                queue.append(nxt)

    return None, None

# =====================================================
# DFS
# =====================================================
def dfs(start, goal, limit=35):

    stack = [(start, 0)]

    visited = set()

    parent = {}

    move_taken = {}

    while stack:

        state, depth = stack.pop()

        if state in visited:
            continue

        visited.add(state)

        if state == goal:

            path = []
            states = []

            cur = goal

            while cur != start:

                states.append(cur)

                path.append(
                    move_taken[cur]
                )

                cur = parent[cur]

            states.append(start)

            states.reverse()
            path.reverse()

            return path, states

        if depth >= limit:
            continue

        for nxt, move in reversed(get_neighbors(state)):

            if nxt not in visited:

                parent[nxt] = state

                move_taken[nxt] = move

                stack.append(
                    (nxt, depth + 1)
                )

    return None, None

# =====================================================
# GUI
# =====================================================
class PuzzleGUI:

    def __init__(self, root):

        self.root = root

        self.root.title("8 Puzzle Visual Solver")

        self.root.geometry("1100x760")

        self.root.configure(bg=BG)

        self.running = False

        # =================================================
        # TITLE
        # =================================================
        tk.Label(
            root,
            text="8 PUZZLE VISUAL SOLVER",
            font=("Arial", 30, "bold"),
            bg=BG,
            fg="#00d4ff"
        ).pack(pady=20)

        # =================================================
        # MAIN FRAME
        # =================================================
        main = tk.Frame(root, bg=FRAME)

        main.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # =================================================
        # LEFT PANEL
        # =================================================
        left = tk.Frame(main, bg=FRAME)

        left.pack(side="left", padx=40)

        # =================================================
        # START STATE
        # =================================================
        tk.Label(
            left,
            text="START STATE",
            font=("Arial", 18, "bold"),
            bg=FRAME,
            fg=TEXT
        ).pack(pady=10)

        self.start_entries = []

        sf = tk.Frame(left, bg=FRAME)
        sf.pack()

        for i in range(3):

            row = []

            for j in range(3):

                e = tk.Entry(
                    sf,
                    width=3,
                    font=("Arial", 28, "bold"),
                    justify="center"
                )

                e.grid(
                    row=i,
                    column=j,
                    padx=5,
                    pady=5
                )

                row.append(e)

            self.start_entries.append(row)

        # =================================================
        # RANDOM BUTTON
        # =================================================
        tk.Button(
            left,
            text="Random Start",
            font=("Arial", 12, "bold"),
            bg=BTN,
            fg="white",
            width=15,
            command=self.random_start
        ).pack(pady=15)

        # =================================================
        # GOAL STATE
        # =================================================
        tk.Label(
            left,
            text="GOAL STATE",
            font=("Arial", 18, "bold"),
            bg=FRAME,
            fg=TEXT
        ).pack(pady=10)

        self.goal_entries = []

        gf = tk.Frame(left, bg=FRAME)
        gf.pack()

        idx = 0

        for i in range(3):

            row = []

            for j in range(3):

                e = tk.Entry(
                    gf,
                    width=3,
                    font=("Arial", 28, "bold"),
                    justify="center"
                )

                val = DEFAULT_GOAL[idx]

                if val != 0:
                    e.insert(0, str(val))

                idx += 1

                e.grid(
                    row=i,
                    column=j,
                    padx=5,
                    pady=5
                )

                row.append(e)

            self.goal_entries.append(row)

        # =================================================
        # BUTTONS
        # =================================================
        bf = tk.Frame(left, bg=FRAME)

        bf.pack(pady=20)

        tk.Button(
            bf,
            text="Solve BFS",
            bg=BTN,
            fg="white",
            width=12,
            command=self.solve_bfs
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            bf,
            text="Solve DFS",
            bg=BTN,
            fg="white",
            width=12,
            command=self.solve_dfs
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            bf,
            text="Reset",
            bg=BTN,
            fg="white",
            width=12,
            command=self.reset
        ).grid(row=0, column=2, padx=10)

        # =================================================
        # RIGHT PANEL
        # =================================================
        right = tk.Frame(main, bg=FRAME)

        right.pack(side="right", padx=40)

        tk.Label(
            right,
            text="VISUALIZATION",
            font=("Arial", 22, "bold"),
            bg=FRAME,
            fg=TEXT
        ).pack(pady=15)

        # =================================================
        # BOARD
        # =================================================
        board = tk.Frame(right, bg=FRAME)

        board.pack()

        self.cells = []

        for i in range(3):

            row = []

            for j in range(3):

                lbl = tk.Label(
                    board,
                    text="",
                    width=4,
                    height=2,
                    font=("Arial", 30, "bold"),
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

        # =================================================
        # STATUS
        # =================================================
        self.status = tk.Label(
            right,
            text="READY",
            font=("Arial", 14, "bold"),
            bg=FRAME,
            fg="#00ff9f"
        )

        self.status.pack(pady=15)

        # =================================================
        # LOG
        # =================================================
        self.log = tk.Text(
            right,
            width=40,
            height=16,
            font=("Consolas", 11),
            bg="#0b1220",
            fg="#00ff9f"
        )

        self.log.pack()

    # =================================================
    # READ STATE
    # =================================================
    def read_state(self, entries):

        nums = []

        try:

            for i in range(3):
                for j in range(3):

                    txt = entries[i][j].get().strip()

                    if txt == "":
                        val = 0
                    else:
                        val = int(txt)

                    nums.append(val)

        except:

            messagebox.showerror(
                "Error",
                "Input phải là số"
            )

            return None

        if sorted(nums) != list(range(9)):

            messagebox.showerror(
                "Error",
                "Phải nhập đủ số từ 0-8"
            )

            return None

        return tuple(nums)

    # =================================================
    # DRAW BOARD
    # =================================================
    def draw_board(self, state):

        for i in range(9):

            r = i // 3
            c = i % 3

            val = state[i]

            if val == 0:

                self.cells[r][c].config(
                    text="",
                    bg=EMPTY
                )

            else:

                self.cells[r][c].config(
                    text=str(val),
                    bg=TILE
                )

        self.root.update()

    # =================================================
    # WRITE LOG
    # =================================================
    def write_log(self, txt):

        self.log.insert(tk.END, txt + "\n")

        self.log.see(tk.END)

    # =================================================
    # RANDOM START
    # =================================================
    def random_start(self):

        if self.running:
            return

        goal = self.read_state(
            self.goal_entries
        )

        if not goal:
            return

        state = generate_random_state(goal)

        idx = 0

        for i in range(3):
            for j in range(3):

                self.start_entries[i][j].delete(
                    0,
                    tk.END
                )

                val = state[idx]

                if val != 0:

                    self.start_entries[i][j].insert(
                        0,
                        str(val)
                    )

                idx += 1

    # =================================================
    # ANIMATE
    # =================================================
    def animate(self, path, states, algo):

        self.running = True

        self.log.delete(1.0, tk.END)

        self.write_log(f"========== {algo} ==========")
        self.write_log(f"Steps : {len(path)}")
        self.write_log(f"Moves : {' '.join(path)}")
        self.write_log("")

        for i, state in enumerate(states):

            self.draw_board(state)

            self.write_log(f"Step {i}")

            for r in range(0, 9, 3):

                self.write_log(
                    str(state[r:r+3])
                )

            self.write_log("")

            time.sleep(0.4)

        self.status.config(
            text=f"{algo} COMPLETED"
        )

        self.running = False

    # =================================================
    # BFS
    # =================================================
    def solve_bfs(self):

        if self.running:
            return

        start = self.read_state(
            self.start_entries
        )

        goal = self.read_state(
            self.goal_entries
        )

        if not start or not goal:
            return

        if not is_solvable(start, goal):

            messagebox.showerror(
                "Error",
                "Unsolvable"
            )

            return

        self.status.config(
            text="RUNNING BFS..."
        )

        def run():

            path, states = bfs(start, goal)

            if path is None:

                messagebox.showinfo(
                    "Result",
                    "No solution"
                )

                return

            self.animate(
                path,
                states,
                "BFS"
            )

        threading.Thread(
            target=run,
            daemon=True
        ).start()

    # =================================================
    # DFS
    # =================================================
    def solve_dfs(self):

        if self.running:
            return

        start = self.read_state(
            self.start_entries
        )

        goal = self.read_state(
            self.goal_entries
        )

        if not start or not goal:
            return

        if not is_solvable(start, goal):

            messagebox.showerror(
                "Error",
                "Unsolvable"
            )

            return

        self.status.config(
            text="RUNNING DFS..."
        )

        def run():

            path, states = dfs(start, goal)

            if path is None:

                messagebox.showinfo(
                    "Result",
                    "DFS depth limit exceeded"
                )

                return

            self.animate(
                path,
                states,
                "DFS"
            )

        threading.Thread(
            target=run,
            daemon=True
        ).start()

    # =================================================
    # RESET
    # =================================================
    def reset(self):

        if self.running:
            return

        # clear log only
        self.log.delete(1.0, tk.END)

        # reset status
        self.status.config(text="RESET")

        # clear visualization only
        for i in range(3):
            for j in range(3):

                self.cells[i][j].config(
                    text="",
                    bg=TILE
                )

# =====================================================
# MAIN
# =====================================================
root = tk.Tk()

app = PuzzleGUI(root)

root.mainloop()