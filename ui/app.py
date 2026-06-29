import threading
import time
import tkinter as tk
import sys
from tkinter import messagebox
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from algo import (
    GOAL,
    START,
    ac3,
    alpha_beta,
    and_or_graph_search,
    astar,
    backtracking,
    belief_bfs,
    best_hill_climbing,
    bfs,
    dfs,
    expectimax,
    forward_checking,
    greedy,
    ida_star,
    ids,
    inv,
    local_beam_search_with_path,
    manhattan,
    neighbors,
    random_hill_climbing,
    random_restart_hill_climbing,
    random_state,
    simulated_annealing,
    simple_hill_climbing,
    solvable,
    ucs,
    minimax,
)


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


class Puzzle:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle AI Solver")
        self.root.geometry("1400x900")
        self.root.config(bg=BG)
        self.running = False
        self.info_mode = "full"

        tk.Label(root, text="8 PUZZLE AI SOLVER", font=("Arial", 28, "bold"),
                 bg=BG, fg="#00d4ff").pack(pady=10)

        main = tk.Frame(root, bg=BG)
        main.pack(fill="both", expand=True, padx=10, pady=5)

        left_container = tk.Frame(main, bg=FRAME)
        left_container.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(left_container, bg=FRAME, highlightthickness=0)
        scrollbar = tk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=FRAME)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.start = self.make_grid(scrollable_frame, "START STATE", START)
        tk.Button(scrollable_frame, text="Random Start", font=("Arial", 11, "bold"), width=18,
                  bg=BTN, fg="white", command=self.random_start).pack(pady=10)

        self.goal = self.make_grid(scrollable_frame, "GOAL STATE", GOAL)

        bf = tk.Frame(scrollable_frame, bg=FRAME)
        bf.pack(pady=15)

        buttons = [
            ("BFS", self.solve_bfs), ("DFS", self.solve_dfs),
            ("IDS", self.solve_ids), ("UCS", self.solve_ucs),
            ("Greedy", self.solve_greedy), ("A*", self.solve_astar),
            ("IDA*", self.solve_ida),
            ("Simple Hill", self.solve_simple_hill), ("Best Hill", self.solve_best_hill),
            ("Random Hill", self.solve_random_hill), ("Random Restart", self.solve_restart_hill),
            ("Local Beam (k=3)", self.solve_beam), ("Simulated Annealing", self.solve_sa),
            ("Belief Search", self.solve_belief_bfs),
            ("AND-OR Graph Search", self.solve_and_or),
            ("Backtracking", self.solve_backtracking), ("Forward Checking", self.solve_forward_checking),
            ("AC-3", self.solve_ac3), ("Minimax", self.solve_minimax),
            ("Alpha-Beta", self.solve_alpha_beta), ("Expectimax", self.solve_expectimax),
            ("RESET", self.reset),
        ]

        for i, (txt, cmd) in enumerate(buttons):
            bg_color = "#ff5f5f" if txt == "RESET" else BTN
            active_color = "#ff7b7b" if txt == "RESET" else BTN_HOVER
            b = tk.Button(bf, text=txt, width=16, height=1, font=("Arial", 9, "bold"),
                          bg=bg_color, fg="white", activebackground=active_color,
                          cursor="hand2", command=cmd)
            b.grid(row=i // 4, column=i % 4, padx=6, pady=6, sticky="nsew")

        reset_btn = tk.Button(scrollable_frame, text="RESET", width=30, height=1,
                              font=("Arial", 12, "bold"), bg="#ff5f5f", fg="white",
                              relief="flat", cursor="hand2", command=self.reset)
        reset_btn.pack(pady=20)

        right = tk.Frame(main, bg=FRAME, bd=2, relief="ridge")
        right.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        title_frame = tk.Frame(right, bg=FRAME)
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="VISUALIZATION", font=("Arial", 22, "bold"),
                 bg=FRAME, fg=TEXT).pack()

        board_frame = tk.Frame(right, bg=FRAME)
        board_frame.pack(pady=10)

        self.board1_frame = tk.Frame(board_frame, bg=FRAME, relief="ridge", bd=2)
        self.board1_frame.pack(side="left", padx=10)
        tk.Label(self.board1_frame, text="State 1", font=("Arial", 12, "bold"), bg=FRAME, fg=TEXT).pack()
        self.cells1 = []
        board1_grid = tk.Frame(self.board1_frame, bg=FRAME)
        board1_grid.pack()
        for i in range(3):
            row = []
            for j in range(3):
                lbl = tk.Label(board1_grid, width=3, height=1, font=("Arial", 28, "bold"),
                               bg=TILE, fg="#111111", relief="ridge", bd=3)
                lbl.grid(row=i, column=j, padx=5, pady=5)
                row.append(lbl)
            self.cells1.append(row)

        self.board2_frame = tk.Frame(board_frame, bg=FRAME, relief="ridge", bd=2)
        self.board2_frame.pack(side="left", padx=10)
        tk.Label(self.board2_frame, text="State 2", font=("Arial", 12, "bold"), bg=FRAME, fg=TEXT).pack()
        self.cells2 = []
        board2_grid = tk.Frame(self.board2_frame, bg=FRAME)
        board2_grid.pack()
        for i in range(3):
            row = []
            for j in range(3):
                lbl = tk.Label(board2_grid, width=3, height=1, font=("Arial", 28, "bold"),
                               bg=TILE, fg="#111111", relief="ridge", bd=3)
                lbl.grid(row=i, column=j, padx=5, pady=5)
                row.append(lbl)
            self.cells2.append(row)
        self.board2_frame.pack_forget()

        self.status = tk.Label(right, text="READY", font=("Arial", 14, "bold"),
                               bg=FRAME, fg=SUCCESS)
        self.status.pack(pady=5)

        self.info = tk.Label(right, text="", font=("Consolas", 14, "bold"),
                             bg=FRAME, fg=INFO)
        self.info.pack(pady=5)

        self.log = tk.Text(right, width=50, height=16, font=("Consolas", 10),
                           bg=LOG_BG, fg=SUCCESS, relief="flat")
        self.log.pack(padx=15, pady=15, fill="both", expand=True)

        self.draw(START)

    def make_grid(self, parent, title, data):
        tk.Label(parent, text=title, font=("Arial", 18, "bold"), bg=FRAME, fg=TEXT).pack(pady=8)
        f = tk.Frame(parent, bg=FRAME)
        f.pack()
        arr = []
        k = 0
        for i in range(3):
            row = []
            for j in range(3):
                e = tk.Entry(f, width=3, font=("Arial", 22, "bold"), justify="center",
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
        except Exception:
            messagebox.showerror("Error", "Please enter numbers 0-8 exactly once")
            return None

    def draw(self, state, board=1, step=None):
        goal = self.read(self.goal)
        cells = self.cells1 if board == 1 else self.cells2
        for i, v in enumerate(state):
            r, c = divmod(i, 3)
            cells[r][c].config(text="" if v == 0 else str(v),
                               bg=EMPTY if v == 0 else TILE)
        if goal:
            g = inv(state) if step is None else step
            h = manhattan(state, goal)
            if self.info_mode == "full":
                self.info.config(text=f"g(n)={g} h(n)={h} f(n)={g+h}")
            elif self.info_mode == "only_h":
                self.info.config(text=f"h(n)={h}")
            elif self.info_mode == "only_g":
                self.info.config(text=f"g(n)={g}")
        self.root.update()

    def draw_belief(self, state1, state2, step=None):
        self.draw(state1, board=1, step=step)
        self.draw(state2, board=2, step=step)

    def write(self, txt):
        self.log.insert(tk.END, txt + "\n")
        self.log.see(tk.END)

    def matrix_lines(self, state):
        return ["   " + str(state[r:r + 3]) for r in range(0, 9, 3)]

    def move_between(self, prev_state, state):
        if prev_state is None or prev_state == state:
            return "START", "trang thai bat dau"
        names = {"U": "o trong di len", "D": "o trong di xuong",
                 "L": "o trong di trai", "R": "o trong di phai"}
        for nxt, mv in neighbors(prev_state):
            if nxt == state:
                return mv, names[mv]
        return "?", "khong xac dinh duoc buoc di"

    def algorithm_detail(self, algo):
        details = {
            "BFS": "BFS duyet theo tung muc do sau, nen buoc hien tai nam tren duong di ngan nhat theo so nuoc di.",
            "DFS": "DFS di sau vao mot nhanh truoc; loi giai phu thuoc thu tu sinh cac trang thai ke.",
            "IDS": "IDS lap DFS voi gioi han do sau tang dan, ket hop tiet kiem bo nho cua DFS va tinh toi uu theo do sau cua BFS.",
            "UCS": "UCS chon trang thai co tong chi phi g nho nhat; voi 8-puzzle moi buoc co chi phi 1.",
            "GREEDY": "Greedy uu tien trang thai co h nho nhat, tuc gan goal nhat theo Manhattan.",
            "A*": "A* can bang chi phi da di g va uoc luong con lai h bang f = g + h.",
            "IDA*": "IDA* tim theo nguong f = g + h, neu vuot nguong thi tang nguong va lap lai.",
            "Simple Hill": "Simple Hill nhan hang xom dau tien lam h giam; neu khong co buoc tot hon thi dung.",
            "Best Hill": "Best Hill xem cac hang xom va chon buoc lam h giam nhieu nhat.",
            "Random Hill": "Random Hill chon ngau nhien trong cac hang xom tot hon hien tai.",
            "Random Restart": "Random Restart chay hill climbing nhieu lan tu cac diem bat dau khac nhau de tranh cuc tri dia phuong.",
            "Local Beam (k=3)": "Local Beam giu k ung vien tot nhat moi vong va mo rong song song cac ung vien do.",
            "Simulated Annealing": "Simulated Annealing co the chap nhan buoc xau theo xac suat phu thuoc nhiet do de thoat cuc tri dia phuong.",
            "AND-OR": "AND-OR o file nay dang dung hang doi uu tien theo heuristic de tim duong di tu start den goal.",
            "Belief Search": "Belief Search ap dung cung mot hanh dong len nhieu trang thai co the xay ra trong belief state.",
            "Backtracking": "Backtracking thu tung buoc di, neu nhanh hien tai khong den goal thi quay lui ve trang thai truoc.",
            "Forward Checking": "Forward Checking giong backtracking nhung loai truoc cac buoc khong con mien gia tri/hang xom hop le.",
            "AC-3": "AC-3 kiem tra tinh nhat quan cung cua cac rang buoc, sau do dung tim kiem de tao duong di tren 8-puzzle.",
            "Minimax": "Minimax danh gia cay nuoc di theo luot MAX/MIN de chon nhanh co diem heuristic tot.",
            "Alpha-Beta": "Alpha-Beta la Minimax co cat tia cac nhanh khong the lam ket qua tot hon.",
            "Expectimax": "Expectimax thay nut doi thu bang nut ky vong, phu hop khi buoc tiep theo co tinh ngau nhien.",
        }
        return details.get(algo, "Thuat toan tao ra chuoi trang thai tu start den goal.")

    def write_state_detail(self, algo, step, state, prev_state, goal, trace_detail=None):
        move, move_text = self.move_between(prev_state, state)
        g = step
        h = manhattan(state, goal) if goal else 0
        prev_h = manhattan(prev_state, goal) if prev_state and goal else h
        delta_h = h - prev_h
        self.write(f"STEP {step}: move={move} | {move_text}")
        if self.info_mode == "full":
            self.write(f"   g(n)={g} h(n)={h} f(n)={g+h} delta_h={delta_h}")
        elif self.info_mode == "only_h":
            self.write(f"   h(n)={h} delta_h={delta_h}")
        else:
            self.write(f"   g(n)={g}")

        if trace_detail and algo == "Simulated Annealing":
            self.write(
                f"   restart={trace_detail.get('restart', '-')} "
                f"iter={trace_detail.get('iteration', '-')} "
                f"temp={trace_detail.get('temp', 0):.4f}"
            )
            self.write(
                f"   h_before={trace_detail.get('current_h', prev_h)} "
                f"h_after={trace_detail.get('next_h', h)} "
                f"accept_prob={trace_detail.get('probability', 1):.4f}"
            )
            self.write(f"   reason: {trace_detail.get('reason', '-')}")
            self.write(f"   rejected candidates before this step: {trace_detail.get('rejected', 0)}")
        elif step == 0:
            self.write("   reason: Khoi tao, chua thuc hien buoc di nao.")
        else:
            self.write(f"   reason: {self.algorithm_detail(algo)}")

        self.write("Matrix:")
        for line in self.matrix_lines(state):
            self.write(line)

    def random_start(self):
        if self.running:
            return
        goal = self.read(self.goal)
        if not goal:
            return
        s = random_state(goal)
        k = 0
        for i in range(3):
            for j in range(3):
                self.start[i][j].delete(0, tk.END)
                if s[k]:
                    self.start[i][j].insert(0, str(s[k]))
                k += 1
        self.draw(s)

    def animate(self, path, states, algo, belief_pairs=None, trace=None):
        self.running = True
        self.log.delete(1.0, tk.END)
        self.write("=" * 45)
        self.write(f"{algo} SOLUTION")
        self.write("=" * 45)
        if path:
            self.write(f"Steps: {len(path)}")
            self.write(f"Moves: {' '.join(path)}\n")
        self.write("Algorithm detail:")
        self.write(self.algorithm_detail(algo))
        self.write("")
        if algo == "Simulated Annealing" and trace:
            last = trace[-1]
            self.write("Simulated Annealing detail:")
            self.write(f"- Restart: {last.get('restart', '-')}")
            self.write(f"- Accepted moves: {len(path) if path else 0}")
            self.write(f"- Best h reached: {last.get('next_h', '-')}")
            self.write("")
        goal = self.read(self.goal)

        if algo in ["A*", "IDA*", "AND-OR", "AC-3", "Minimax", "Alpha-Beta", "Expectimax"]:
            self.info_mode = "full"
        elif algo in ["GREEDY", "Simple Hill", "Best Hill", "Random Hill",
                      "Random Restart", "Local Beam (k=3)", "Simulated Annealing"]:
            self.info_mode = "only_h"
        else:
            self.info_mode = "only_g"

        if belief_pairs is not None:
            self.board2_frame.pack(side="left", padx=10)
            for i, (s1, s2) in enumerate(belief_pairs):
                self.draw_belief(s1, s2, step=i)
                g1 = i
                g2 = i
                h1 = manhattan(s1, goal) if goal else 0
                h2 = manhattan(s2, goal) if goal else 0
                action = "START" if i == 0 or not path else path[i - 1]
                action_text = {
                    "U": "ap dung hanh dong len",
                    "D": "ap dung hanh dong xuong",
                    "L": "ap dung hanh dong trai",
                    "R": "ap dung hanh dong phai",
                    "START": "belief state ban dau",
                }.get(action, "ap dung hanh dong")
                if self.info_mode == "full":
                    self.write(f"STEP {i}: State1 g={g1} h={h1} f={g1+h1}")
                    self.write(f"       State2 g={g2} h={h2} f={g2+h2}")
                elif self.info_mode == "only_h":
                    self.write(f"STEP {i}: State1 h={h1}, State2 h={h2}")
                else:
                    self.write(f"STEP {i}: State1 depth={g1}, State2 depth={g2}")
                self.write(f"Action: {action} - {action_text}")
                self.write(f"Reason: {self.algorithm_detail(algo)}")
                if i > 0:
                    p1, p2 = belief_pairs[i - 1]
                    mv1, text1 = self.move_between(p1, s1)
                    mv2, text2 = self.move_between(p2, s2)
                    self.write(f"State1 transition: {mv1} - {text1}; delta_h={h1 - manhattan(p1, goal)}")
                    self.write(f"State2 transition: {mv2} - {text2}; delta_h={h2 - manhattan(p2, goal)}")
                self.write("State1 matrix:")
                for line in self.matrix_lines(s1):
                    self.write(line)
                self.write("State2 matrix:")
                for line in self.matrix_lines(s2):
                    self.write(line)
                self.write("-" * 40)
                time.sleep(0.35)
            self.board2_frame.pack_forget()
        else:
            self.board2_frame.pack_forget()
            if states:
                for i, s in enumerate(states):
                    self.draw(s, step=i)
                    detail = trace[i] if trace and i < len(trace) else None
                    prev_state = states[i - 1] if i > 0 else None
                    self.write_state_detail(algo, i, s, prev_state, goal, detail)
                    self.write("-" * 40)
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
            else:
                trace = getattr(solver_func, "last_trace", None)
                if algo != "Simulated Annealing":
                    trace = None
                self.animate(path, states, algo, trace=trace)

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

    def solve_ida(self):
        self.solve("IDA*", ida_star)

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

    def solve_sa(self):
        self.solve("Simulated Annealing", simulated_annealing)

    def solve_and_or(self):
        self.solve("AND-OR", and_or_graph_search)

    def solve_backtracking(self):
        self.solve("Backtracking", backtracking)

    def solve_forward_checking(self):
        self.solve("Forward Checking", forward_checking)

    def solve_ac3(self):
        self.solve("AC-3", ac3)

    def solve_minimax(self):
        self.solve("Minimax", minimax)

    def solve_alpha_beta(self):
        self.solve("Alpha-Beta", alpha_beta)

    def solve_expectimax(self):
        self.solve("Expectimax", expectimax)

    def solve_belief_bfs(self):
        if self.running:
            return
        goal = self.read(self.goal)
        if not goal:
            messagebox.showerror("Error", "Please enter goal state")
            return
        s1 = (1, 2, 3, 8, 4, 5, 7, 6, 0)
        s2 = (1, 2, 3, 8, 4, 5, 7, 0, 6)
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

    def reset(self):
        if self.running:
            return
        self.info_mode = "full"
        self.log.delete(1.0, tk.END)
        self.status.config(text="RESET")
        self.draw(START)
        self.board2_frame.pack_forget()


def run_app():
    root = tk.Tk()
    app = Puzzle(root)
    root.mainloop()
    return app


if __name__ == "__main__":
    run_app()
