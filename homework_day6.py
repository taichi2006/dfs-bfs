import tkinter as tk
from tkinter import messagebox
import random, threading, time

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

    for dr, dc, mv in [(-1,0,'U'),(1,0,'D'),(0,-1,'L'),(0,1,'R')]:
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

# ================= IDS =================
def dls(start, goal, limit):
    stack = [(start, 0)]
    parent = {start: (None, None)}

    while stack:

        cur, depth = stack.pop()

        if cur == goal:
            break

        if depth >= limit:
            continue

        for nxt, mv in reversed(list(neighbors(cur))):
            if nxt not in parent:
                parent[nxt] = (cur, mv)
                stack.append((nxt, depth + 1))

    if goal not in parent:
        return None, None

    path, states = [], []
    cur = goal

    while cur:
        states.append(cur)
        p, mv = parent[cur]
        if mv:
            path.append(mv)
        cur = p

    return path[::-1], states[::-1]


def ids(start, goal, max_depth=30):
    for limit in range(max_depth + 1):
        path, states = dls(start, goal, limit)
        if path is not None:
            return path, states
    return None, None

# ================= GUI =================
class Puzzle:

    def __init__(self, root):

        self.root = root
        self.root.title("8 Puzzle IDS Solver")
        self.root.geometry("950x700")
        self.root.config(bg=BG)

        self.running = False

        tk.Label(
            root,
            text="8 PUZZLE IDS SOLVER",
            font=("Arial",28,"bold"),
            bg=BG,
            fg="#00d4ff"
        ).pack(pady=15)

        main = tk.Frame(root, bg=FRAME)
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # ============ LEFT ============
        left = tk.Frame(main, bg=FRAME)
        left.pack(side="left", padx=30)

        self.start = self.make_grid(left, "START STATE", START)

        tk.Button(
            left,
            text="Random Start",
            bg=BTN,
            fg="white",
            width=18,
            command=self.random_start
        ).pack(pady=15)

        self.goal = self.make_grid(left, "GOAL STATE", GOAL)

        bf = tk.Frame(left, bg=FRAME)
        bf.pack(pady=20)

        tk.Button(
            bf,
            text="Solve IDS",
            bg=BTN,
            fg="white",
            width=12,
            command=self.solve_ids
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            bf,
            text="Reset",
            bg=BTN,
            fg="white",
            width=12,
            command=self.reset
        ).grid(row=0, column=1, padx=8)

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
                lbl.grid(row=i,column=j,padx=6,pady=6)
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
            width=38,
            height=15,
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
                e.grid(row=i,column=j,padx=5,pady=5)
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
                    nums.append(0 if t == "" else int(t))

            if sorted(nums) != list(range(9)):
                raise ValueError

            return tuple(nums)

        except:
            messagebox.showerror("Error", "Nhập đủ số 0-8")
            return None

    # ================= DRAW =================
    def draw(self, state):
        for i,v in enumerate(state):
            r,c = divmod(i,3)
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
    def animate(self, path, states):
        self.running = True
        self.log.delete(1.0, tk.END)

        self.write("IDS SOLUTION")
        self.write(f"Steps: {len(path)}")
        self.write(f"Moves: {' '.join(path)}\n")

        for i, s in enumerate(states):
            self.draw(s)
            self.write(f"Step {i}: {s}")
            time.sleep(0.4)

        self.status.config(text="IDS COMPLETED")
        self.running = False

    # ================= IDS SOLVER =================
    def solve_ids(self):

        if self.running:
            return

        start = self.read(self.start)
        goal = self.read(self.goal)

        if not start or not goal:
            return

        if not solvable(start, goal):
            messagebox.showerror("Error", "Unsolvable")
            return

        self.status.config(text="RUNNING IDS...")

        def run():
            path, states = ids(start, goal)

            if path is None:
                messagebox.showinfo("Result", "No Solution")
                return

            self.animate(path, states)

        threading.Thread(target=run, daemon=True).start()

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