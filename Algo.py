"""
AI2002 - Artificial Intelligence | Assignment 1

Author: Waseem Akhtar
Roll No: 22I-1226
Section: B

"""

import tkinter as tk
from tkinter import messagebox
import math

# ══════════════════════════════════════════════════════════════
#  VISUAL THEME COLORS
# ══════════════════════════════════════════════════════════════
C_FREE      = "#FFFFFF"
C_BLOCKED   = "#2C2C2C"
C_START     = "#27AE60"
C_GOAL      = "#E74C3C"
C_VISITED   = "#AED6F1"
C_PATH      = "#F4D03F"
C_GRID_LINE = "#BDC3C7"
C_BG        = "#1C2833"
C_PANEL     = "#2E4053"
C_TEXT      = "#ECF0F1"
C_HEAD      = "#F39C12"
C_BTN_RUN   = "#27AE60"
C_BTN_CLR   = "#E67E22"
C_BTN_RST   = "#C0392B"

# ══════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════
CELL_SZ      = 36
MIN_DIM      = 10
MAX_DIM      = 50
DEF_ROWS     = 15
DEF_COLS     = 20
ANIM_MS      = 22
DEFAULT_COST = 1

FREE    = 0
BLOCKED = 1

DIRS = ((-1,0), (1,0), (0,-1), (0,1))  # up, down, left, right ONLY


# ══════════════════════════════════════════════════════════════
#  MANUAL DATA STRUCTURES
# ══════════════════════════════════════════════════════════════

class Queue:
    """FIFO queue"""
    def __init__(self, cap):
        self._data = [None] * cap
        self._front = 0
        self._rear = 0
        self._cap = cap
    
    def enqueue(self, item):
        if self._rear >= self._cap:
            raise OverflowError("Queue full")
        self._data[self._rear] = item
        self._rear = self._rear + 1
    
    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue empty")
        item = self._data[self._front]
        self._data[self._front] = None
        self._front = self._front + 1
        return item
    
    def is_empty(self):
        return self._front == self._rear


class Stack:
    """LIFO stack"""
    def __init__(self, cap):
        self._data = [None] * cap
        self._top = 0
        self._cap = cap
    
    def push(self, item):
        if self._top >= self._cap:
            raise OverflowError("Stack full")
        self._data[self._top] = item
        self._top = self._top + 1
    
    def pop(self):
        if self.is_empty():
            raise IndexError("Stack empty")
        self._top = self._top - 1
        item = self._data[self._top]
        self._data[self._top] = None
        return item
    
    def is_empty(self):
        return self._top == 0


class MinHeap:
    """
    Binary min-heap 
    """
    def __init__(self, cap):
        self._data = [None] * cap
        self._size = 0
        self._cap = cap
    
    @staticmethod
    def _compare(a, b):
        """Return True if a has higher priority than b"""
        # Primary: lower value = higher priority
        if a[0] != b[0]:
            return a[0] < b[0]
        # Tie-break: for A*, prefer lower g (second element)
        if len(a) > 1 and len(b) > 1:
            if isinstance(a[1], (int, float)) and isinstance(b[1], (int, float)):
                return a[1] < b[1]
        return False
    
    def _swap(self, i, j):
        temp = self._data[i]
        self._data[i] = self._data[j]
        self._data[j] = temp
    
    def _parent_idx(self, i):
        return (i - 1) // 2
    
    def _left_idx(self, i):
        return 2 * i + 1
    
    def _right_idx(self, i):
        return 2 * i + 2
    
    def _bubble_up(self, idx):
        while idx > 0:
            p = self._parent_idx(idx)
            if self._compare(self._data[idx], self._data[p]):
                self._swap(idx, p)
                idx = p
            else:
                break
    
    def _bubble_down(self, idx):
        while True:
            smallest = idx
            left = self._left_idx(idx)
            right = self._right_idx(idx)
            
            if left < self._size and self._compare(self._data[left], self._data[smallest]):
                smallest = left
            if right < self._size and self._compare(self._data[right], self._data[smallest]):
                smallest = right
            
            if smallest != idx:
                self._swap(idx, smallest)
                idx = smallest
            else:
                break
    
    def push(self, item):
        if self._size >= self._cap:
            raise OverflowError("Heap full")
        self._data[self._size] = item
        self._bubble_up(self._size)
        self._size = self._size + 1
    
    def pop(self):
        if self.is_empty():
            raise IndexError("Heap empty")
        top = self._data[0]
        self._size = self._size - 1
        self._data[0] = self._data[self._size]
        self._data[self._size] = None
        if self._size > 0:
            self._bubble_down(0)
        return top
    
    def is_empty(self):
        return self._size == 0


# ══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════

def _in_bounds(r, c, rows, cols):
    """Check if (r,c) is within grid bounds"""
    return 0 <= r < rows and 0 <= c < cols


def _build_2d_array(rows, cols, init_value):
    """
    Build 2D array manually without list multiplication

    """
    result = []
    for r in range(rows):
        row = []
        for c in range(cols):
            row = row + [init_value]  # concatenation (no append)
        result = result + [row]
    return result


def _reconstruct_path(parent, goal, rows, cols):
    """Reconstruct path from goal to start using parent pointers"""
    cap = rows * cols
    stk = Stack(cap)
    cur = goal
    
    while cur is not None:
        stk.push(cur)
        r, c = cur
        cur = parent[r][c]
    
    path = []
    while not stk.is_empty():
        path = path + [stk.pop()]
    
    return path


# ══════════════════════════════════════════════════════════════
#  Q1 - BFS ALGORITHM
# ══════════════════════════════════════════════════════════════

def run_bfs(grid, rows, cols, start, goal):
    """
    Breadth-First Search
    
    """
    cap = rows * cols
    frontier = Queue(cap)
    
    # Build visited grid manually
    visited = _build_2d_array(rows, cols, False)
    
    # Build parent grid manually
    parent = _build_2d_array(rows, cols, None)
    
    sr, sc = start
    gr, gc = goal
    
    # Enqueue start and mark visited immediately
    frontier.enqueue((sr, sc))
    visited[sr][sc] = True
    
    # Track visit order manually
    vis_arr = [None] * cap
    vis_cnt = 0
    vis_arr[vis_cnt] = (sr, sc)
    vis_cnt = vis_cnt + 1
    
    found = False
    
    while not frontier.is_empty():
        r, c = frontier.dequeue()
        
        if r == gr and c == gc:
            found = True
            break
        
        # Explore 4 neighbors
        for dr, dc in DIRS:
            nr = r + dr
            nc = c + dc
            
            # Boundary check
            if not _in_bounds(nr, nc, rows, cols):
                continue
            
            # Blocked cells NEVER enqueued
            if grid[nr][nc] == BLOCKED:
                continue
            
            # Mark visited when enqueued (BFS requirement)
            if not visited[nr][nc]:
                visited[nr][nc] = True
                parent[nr][nc] = (r, c)
                frontier.enqueue((nr, nc))
                vis_arr[vis_cnt] = (nr, nc)
                vis_cnt = vis_cnt + 1
    
    # Build visited list
    vis_list = []
    for i in range(vis_cnt):
        vis_list = vis_list + [vis_arr[i]]
    
    if not found:
        return None, vis_list
    
    return _reconstruct_path(parent, goal, rows, cols), vis_list


# ══════════════════════════════════════════════════════════════
#  Q1 - DFS ALGORITHM
# ══════════════════════════════════════════════════════════════

def run_dfs(grid, rows, cols, start, goal):
    """
    Depth-First Search (iterative, stack-based)
    
    """
    cap = rows * cols
    frontier = Stack(cap)
    
    visited = _build_2d_array(rows, cols, False)
    parent = _build_2d_array(rows, cols, None)
    
    sr, sc = start
    gr, gc = goal
    
    frontier.push((sr, sc))
    
    vis_arr = [None] * cap
    vis_cnt = 0
    found = False
    
    # Reversed directions so first dir stays on top of stack
    DIRS_REV = ((0,1), (0,-1), (1,0), (-1,0))
    
    while not frontier.is_empty():
        r, c = frontier.pop()
        
        # Skip if already processed (duplicate pushes happen in DFS)
        if visited[r][c]:
            continue
        
        # Mark visited when POPPED
        visited[r][c] = True
        vis_arr[vis_cnt] = (r, c)
        vis_cnt = vis_cnt + 1
        
        if r == gr and c == gc:
            found = True
            break
        
        for dr, dc in DIRS_REV:
            nr = r + dr
            nc = c + dc
            
            if not _in_bounds(nr, nc, rows, cols):
                continue
            
            # Blocked cells NEVER pushed
            if grid[nr][nc] == BLOCKED:
                continue
            
            if not visited[nr][nc]:
                # Record parent on first discovery
                if parent[nr][nc] is None and (nr, nc) != start:
                    parent[nr][nc] = (r, c)
                frontier.push((nr, nc))
    
    vis_list = []
    for i in range(vis_cnt):
        vis_list = vis_list + [vis_arr[i]]
    
    if not found:
        return None, vis_list
    
    return _reconstruct_path(parent, goal, rows, cols), vis_list


# ══════════════════════════════════════════════════════════════
#  Q2 - UNIFORM COST SEARCH (UCS)
# ══════════════════════════════════════════════════════════════

def run_ucs(grid, rows, cols, start, goal, cost_grid):
    """
    Uniform Cost Search
    
    """
    cap = rows * cols * 4  # allow re-insertions
    frontier = MinHeap(cap)
    
    INF = float('inf')
    g_cost = _build_2d_array(rows, cols, INF)
    parent = _build_2d_array(rows, cols, None)
    expanded = _build_2d_array(rows, cols, False)
    
    sr, sc = start
    gr, gc = goal
    
    g_cost[sr][sc] = 0
    frontier.push((0, (sr, sc)))  # (g, position)
    
    vis_arr = [None] * cap
    vis_cnt = 0
    found = False
    total = 0
    
    while not frontier.is_empty():
        g, pos = frontier.pop()
        r, c = pos
        
        # Skip if already expanded (lazy deletion)
        if expanded[r][c]:
            continue
        
        expanded[r][c] = True
        vis_arr[vis_cnt] = (r, c)
        vis_cnt = vis_cnt + 1
        
        if r == gr and c == gc:
            found = True
            total = g
            break
        
        for dr, dc in DIRS:
            nr = r + dr
            nc = c + dc
            
            if not _in_bounds(nr, nc, rows, cols):
                continue
            
            # Blocked cells NEVER inserted
            if grid[nr][nc] == BLOCKED:
                continue
            
            # Cost = cumulative + destination cell cost
            new_g = g + cost_grid[nr][nc]
            
            # Re-insert if cheaper path found
            if new_g < g_cost[nr][nc]:
                g_cost[nr][nc] = new_g
                parent[nr][nc] = (r, c)
                frontier.push((new_g, (nr, nc)))
    
    vis_list = []
    for i in range(vis_cnt):
        vis_list = vis_list + [vis_arr[i]]
    
    if not found:
        return None, vis_list, 0
    
    return _reconstruct_path(parent, goal, rows, cols), vis_list, total


# ══════════════════════════════════════════════════════════════
#  Q3 - A* SEARCH
# ══════════════════════════════════════════════════════════════

def run_astar(grid, rows, cols, start, goal, heuristic_type):
    """
    A* Search with Manhattan or Euclidean heuristic
    
    """
    gr, gc = goal
    
    # Heuristic functions (both admissible)
    if heuristic_type == "manhattan":
        def h(r, c):
            return abs(r - gr) + abs(c - gc)
    else:  # euclidean
        def h(r, c):
            return math.sqrt((r - gr) * (r - gr) + (c - gc) * (c - gc))
    
    cap = rows * cols * 4
    frontier = MinHeap(cap)
    
    INF = float('inf')
    g_cost = _build_2d_array(rows, cols, INF)
    parent = _build_2d_array(rows, cols, None)
    closed = _build_2d_array(rows, cols, False)
    
    sr, sc = start
    
    g_cost[sr][sc] = 0
    h_start = h(sr, sc)
    frontier.push((h_start, 0, (sr, sc)))  # (f, g, position)
    
    vis_arr = [None] * cap
    vis_cnt = 0
    found = False
    
    while not frontier.is_empty():
        f, g, pos = frontier.pop()
        r, c = pos
        
        # Skip if already in closed set
        if closed[r][c]:
            continue
        
        closed[r][c] = True
        vis_arr[vis_cnt] = (r, c)
        vis_cnt = vis_cnt + 1
        
        if r == gr and c == gc:
            found = True
            break
        
        for dr, dc in DIRS:
            nr = r + dr
            nc = c + dc
            
            if not _in_bounds(nr, nc, rows, cols):
                continue
            
            # Blocked cells NEVER inserted
            if grid[nr][nc] == BLOCKED:
                continue
            
            # Skip already expanded
            if closed[nr][nc]:
                continue
            
            # Movement cost = 1
            tentative_g = g + 1
            
            if tentative_g < g_cost[nr][nc]:
                g_cost[nr][nc] = tentative_g
                parent[nr][nc] = (r, c)
                h_val = h(nr, nc)
                f_new = tentative_g + h_val
                frontier.push((f_new, tentative_g, (nr, nc)))
    
    vis_list = []
    for i in range(vis_cnt):
        vis_list = vis_list + [vis_arr[i]]
    
    if not found:
        return None, vis_list
    
    return _reconstruct_path(parent, goal, rows, cols), vis_list


# ══════════════════════════════════════════════════════════════
#  GUI APPLICATION
# ══════════════════════════════════════════════════════════════

class PathfindingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI2002 - Waseem Akhtar (22I-1226) - Pathfinding")
        self.root.configure(bg=C_BG)
        
        self.rows = DEF_ROWS
        self.cols = DEF_COLS
        self.grid = []
        self.costs = []
        self.rects = []
        self.start = None
        self.goal = None
        
        self.mode = tk.StringVar(value="block")
        self.algo = tk.StringVar(value="BFS")
        
        self._anim_id = None
        self._build_ui()
        self._init_grid()
    
    def _build_ui(self):
        # Left panel
        panel = tk.Frame(self.root, bg=C_PANEL, width=230)
        panel.pack(side=tk.LEFT, fill=tk.Y)
        panel.pack_propagate(False)
        
        self._panel_grid(panel)
        self._panel_cost(panel)
        self._panel_mode(panel)
        self._panel_algo(panel)
        self._panel_controls(panel)
        self._panel_status(panel)
        
        # Canvas
        cf = tk.Frame(self.root, bg=C_BG)
        cf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(cf, bg="#0D1117", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
    
    def _sec(self, p, txt):
        tk.Label(p, text=txt, bg=C_PANEL, fg=C_HEAD,
                font=("Consolas",9,"bold")).pack(anchor="w",padx=12,pady=(8,2))
    
    def _btn(self, p, txt, cmd, bg):
        b = tk.Button(p, text=txt, command=cmd, bg=bg, fg="white",
                     relief="flat", font=("Consolas",9,"bold"),
                     cursor="hand2", padx=8, pady=5)
        b.pack(fill=tk.X, padx=12, pady=3)
    
    def _panel_grid(self, p):
        self._sec(p, "⚙ Grid Size")
        f = tk.Frame(p, bg=C_PANEL)
        f.pack(padx=12, pady=2)
        tk.Label(f, text="R:", bg=C_PANEL, fg=C_TEXT,
                font=("Consolas",9)).grid(row=0,column=0)
        self.e_rows = tk.Entry(f, width=4, bg="#0D1117", fg=C_TEXT,
                              font=("Consolas",9))
        self.e_rows.insert(0, str(DEF_ROWS))
        self.e_rows.grid(row=0, column=1, padx=3)
        tk.Label(f, text="C:", bg=C_PANEL, fg=C_TEXT,
                font=("Consolas",9)).grid(row=0,column=2,padx=(8,0))
        self.e_cols = tk.Entry(f, width=4, bg="#0D1117", fg=C_TEXT,
                              font=("Consolas",9))
        self.e_cols.insert(0, str(DEF_COLS))
        self.e_cols.grid(row=0, column=3, padx=3)
        self._btn(p, "Create Grid", self._apply_size, "#2980B9")
    
    def _panel_cost(self, p):
        self._sec(p, "💲 UCS Cell Cost")
        f = tk.Frame(p, bg=C_PANEL)
        f.pack(padx=12, pady=2)
        tk.Label(f, text="Cost:", bg=C_PANEL, fg=C_TEXT,
                font=("Consolas",9)).grid(row=0,column=0)
        self.e_cost = tk.Entry(f, width=4, bg="#0D1117", fg=C_TEXT,
                              font=("Consolas",9))
        self.e_cost.insert(0, "1")
        self.e_cost.grid(row=0, column=1, padx=3)
    
    def _panel_mode(self, p):
        self._sec(p, "✏ Edit Mode")
        for txt,val in [("Block/Free","block"),("Start","start"),
                       ("Goal","goal"),("Set Cost","cost")]:
            tk.Radiobutton(p, text=txt, variable=self.mode, value=val,
                          bg=C_PANEL, fg=C_TEXT, selectcolor="#0D1117",
                          font=("Consolas",9)).pack(anchor="w",padx=18,pady=1)
    
    def _panel_algo(self, p):
        self._sec(p, "🔍 Algorithm")
        for txt,val in [("BFS","BFS"),("DFS","DFS"),("UCS","UCS"),
                       ("A* Manhattan","ASTAR_M"),("A* Euclidean","ASTAR_E")]:
            tk.Radiobutton(p, text=txt, variable=self.algo, value=val,
                          bg=C_PANEL, fg=C_TEXT, selectcolor="#0D1117",
                          font=("Consolas",9,"bold")).pack(anchor="w",padx=18,pady=2)
    
    def _panel_controls(self, p):
        self._sec(p, "▶ Controls")
        self._btn(p, "▶ Run", self._run, C_BTN_RUN)
        self._btn(p, "✕ Clear", self._clear, C_BTN_CLR)
        self._btn(p, "⟳ Reset", self._reset, C_BTN_RST)
    
    def _panel_status(self, p):
        self._sec(p, "ℹ Status")
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(p, textvariable=self.status_var, bg=C_PANEL, fg=C_TEXT,
                font=("Consolas",8), wraplength=210,
                justify="left").pack(anchor="w", padx=12, pady=4)
    
    def _init_grid(self):
        self.grid = _build_2d_array(self.rows, self.cols, FREE)
        self.costs = _build_2d_array(self.rows, self.cols, DEFAULT_COST)
        self.rects = _build_2d_array(self.rows, self.cols, None)
        self.start = None
        self.goal = None
        self._draw_all()
    
    def _draw_all(self):
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                self._draw_cell(r, c)
    
    def _cell_color(self, r, c):
        if self.start and (r,c)==self.start: return C_START
        if self.goal and (r,c)==self.goal: return C_GOAL
        if self.grid[r][c]==BLOCKED: return C_BLOCKED
        return C_FREE
    
    def _draw_cell(self, r, c, override=None):
        x1 = c * CELL_SZ
        y1 = r * CELL_SZ
        x2 = x1 + CELL_SZ
        y2 = y1 + CELL_SZ
        clr = override if override else self._cell_color(r,c)
        
        if self.rects[r][c]:
            self.canvas.delete(self.rects[r][c])
        
        rect = self.canvas.create_rectangle(x1,y1,x2,y2,
                                           fill=clr, outline=C_GRID_LINE)
        self.rects[r][c] = rect
        
        lbl = ""
        if self.start and (r,c)==self.start: lbl = "S"
        if self.goal and (r,c)==self.goal: lbl = "G"
        if lbl:
            self.canvas.create_text(x1+CELL_SZ//2, y1+CELL_SZ//2,
                                   text=lbl, fill="white",
                                   font=("Consolas",12,"bold"))
    
    def _apply_size(self):
        try:
            r = int(self.e_rows.get())
            c = int(self.e_cols.get())
        except ValueError:
            messagebox.showerror("Error", "Enter integers")
            return
        if not (MIN_DIM<=r<=MAX_DIM) or not (MIN_DIM<=c<=MAX_DIM):
            messagebox.showerror("Error", f"Size must be {MIN_DIM}-{MAX_DIM}")
            return
        self.rows = r
        self.cols = c
        self._cancel_anim()
        self._init_grid()
    
    def _cell_at(self, x, y):
        c = x // CELL_SZ
        r = y // CELL_SZ
        if _in_bounds(r,c,self.rows,self.cols):
            return r,c
        return None
    
    def _on_click(self, event):
        pos = self._cell_at(event.x, event.y)
        if pos: self._handle_click(*pos)
    
    def _on_drag(self, event):
        pos = self._cell_at(event.x, event.y)
        if pos and self.mode.get()=="block":
            r,c = pos
            if (r,c)!=self.start and (r,c)!=self.goal:
                if self.grid[r][c]==FREE:
                    self.grid[r][c]=BLOCKED
                    self._draw_cell(r,c)
    
    def _handle_click(self, r, c):
        mode = self.mode.get()
        
        if mode=="block":
            if (r,c)==self.start or (r,c)==self.goal: return
            self.grid[r][c] = BLOCKED if self.grid[r][c]==FREE else FREE
            self._draw_cell(r,c)
        
        elif mode=="start":
            if self.start: self._draw_cell(*self.start)
            self.grid[r][c] = FREE
            self.start = (r,c)
            self._draw_cell(r,c)
        
        elif mode=="goal":
            if self.goal: self._draw_cell(*self.goal)
            self.grid[r][c] = FREE
            self.goal = (r,c)
            self._draw_cell(r,c)
        
        elif mode=="cost":
            if self.grid[r][c]==BLOCKED:
                messagebox.showwarning("Blocked", "Can't set cost on blocked cell")
                return
            try:
                cost = int(self.e_cost.get())
                if cost < 1: raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Cost must be positive integer")
                return
            self.costs[r][c] = cost
            self._draw_cell(r,c)
    
    def _run(self):
        if not self.start or not self.goal:
            messagebox.showwarning("Missing", "Set start and goal first")
            return
        
        self._cancel_anim()
        self._clear_vis()
        
        alg = self.algo.get()
        
        if alg == "BFS":
            path, vis = run_bfs(self.grid, self.rows, self.cols,
                               self.start, self.goal)
            self._animate(vis, path, alg, None)
        
        elif alg == "DFS":
            path, vis = run_dfs(self.grid, self.rows, self.cols,
                               self.start, self.goal)
            self._animate(vis, path, alg, None)
        
        elif alg == "UCS":
            path, vis, cost = run_ucs(self.grid, self.rows, self.cols,
                                     self.start, self.goal, self.costs)
            self._animate(vis, path, alg, cost)
        
        elif alg == "ASTAR_M":
            path, vis = run_astar(self.grid, self.rows, self.cols,
                                 self.start, self.goal, "manhattan")
            self._animate(vis, path, alg, None)
        
        elif alg == "ASTAR_E":
            path, vis = run_astar(self.grid, self.rows, self.cols,
                                 self.start, self.goal, "euclidean")
            self._animate(vis, path, alg, None)
    
    def _animate(self, visited, path, alg, extra):
        steps = []
        
        for cell in visited:
            if cell!=self.start and cell!=self.goal:
                steps = steps + [(cell[0], cell[1], C_VISITED)]
        
        if path:
            for cell in path:
                if cell!=self.start and cell!=self.goal:
                    steps = steps + [(cell[0], cell[1], C_PATH)]
        
        self._anim_steps = steps
        self._anim_idx = 0
        self._anim_path = path
        self._anim_alg = alg
        self._anim_extra = extra
        self._anim_vis_n = len([v for v in visited
                               if v!=self.start and v!=self.goal])
        self._anim_tick()
    
    def _anim_tick(self):
        if self._anim_idx >= len(self._anim_steps):
            self._anim_done()
            return
        r,c,clr = self._anim_steps[self._anim_idx]
        self.canvas.itemconfig(self.rects[r][c], fill=clr)
        self._anim_idx = self._anim_idx + 1
        self._anim_id = self.root.after(ANIM_MS, self._anim_tick)
    
    def _anim_done(self):
        if self.start: self._draw_cell(*self.start)
        if self.goal: self._draw_cell(*self.goal)
        
        alg = self._anim_alg
        path = self._anim_path
        extra = self._anim_extra
        vis_n = self._anim_vis_n
        
        if path is None:
            msg = f"{alg}:  No path\nGoal unreachable\nVisited: {vis_n}"
            self.status_var.set(msg)
            messagebox.showinfo("No Path", f"{alg}: Goal unreachable")
        else:
            steps = len(path) - 1
            # ✅ FIX: Display UCS total cost (5 marks requirement)
            if extra is not None:
                msg = f"{alg}:  Found!\nSteps: {steps}\n💲 TOTAL COST: {extra}\nVisited: {vis_n}"
            else:
                msg = f"{alg}:  Found!\nSteps: {steps}\nVisited: {vis_n}"
            self.status_var.set(msg)
    
    def _clear(self):
        self._cancel_anim()
        self._clear_vis()
    
    def _reset(self):
        self._cancel_anim()
        self._init_grid()
    
    def _clear_vis(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self._draw_cell(r,c)
    
    def _cancel_anim(self):
        if self._anim_id:
            self.root.after_cancel(self._anim_id)
            self._anim_id = None


def main():
    root = tk.Tk()
    w = DEF_COLS * CELL_SZ + 260
    h = max(DEF_ROWS * CELL_SZ + 60, 680)
    root.geometry(f"{w}x{h}")
    PathfindingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
