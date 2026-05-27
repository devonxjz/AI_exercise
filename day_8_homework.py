import random
import heapq
import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class EightPuzzle:
    """
    Model: Tracks the state of the 3x3 8-puzzle board and manages A* search.
    States are represented as 3x3 tuples of tuples (hashable, immutable).
    0 represents the empty cell.
    """
    def __init__(self, start_state=None):
        self.goal_state = ((1, 2, 3), 
                           (4, 5, 6), 
                           (7, 8, 0))
        
        if start_state is not None:
            # Ensure it is a tuple of tuples
            self.current_state = tuple(tuple(row) for row in start_state)
        else:
            self.current_state = self.generate_random_solvable()
            
        self.start_state = self.current_state
        
        # Search state variables
        self.frontier = []        # Priority queue containing: (f, counter, g, h, state_grid)
        self.explored = set()     # Closed List: set of grids
        self.parent_map = {}      # Maps: neighbor_grid -> (parent_grid, action)
        self.counter = 0          # Incrementing counter for heapq tie-breaking
        self.state = "idle"       # "idle", "searching", "solved", "unsolvable"
        
        # Statistics
        self.nodes_expanded = 0
        self.max_frontier_size = 0
        self.solution_path = []
        self.path_cost = 0

    def count_inversions(self, grid):
        """
        Calculates the number of inversions in the grid (ignoring the blank tile 0).
        An inversion is any pair (a, b) such that a > b and a appears before b.
        """
        flat = [val for row in grid for val in row if val != 0]
        inversions = 0
        for i in range(len(flat)):
            for j in range(i + 1, len(flat)):
                if flat[i] > flat[j]:
                    inversions += 1
        return inversions

    def is_solvable(self, grid):
        """
        For a standard goal state where the blank is in the bottom-right corner
        (which has 0 inversions - even), an initial state is solvable if and only if
        the number of inversions is even.
        """
        return self.count_inversions(grid) % 2 == 0

    def generate_random_solvable(self):
        """
        Shuffles the tiles randomly until a mathematically solvable configuration is found.
        """
        while True:
            nums = list(range(9))
            random.shuffle(nums)
            grid = tuple(tuple(nums[i*3 : (i+1)*3]) for i in range(3))
            if self.is_solvable(grid):
                return grid

    def get_misplaced_tiles(self, grid):
        """
        Heuristic h(n): counts the number of non-zero tiles that are not in their
        correct goal position.
        """
        count = 0
        for r in range(3):
            for c in range(3):
                val = grid[r][c]
                if val != 0 and val != self.goal_state[r][c]:
                    count += 1
        return count

    def get_neighbors(self, grid):
        """
        Finds the empty tile 0 and moves it in valid directions (UP, DOWN, LEFT, RIGHT).
        Returns a list of tuples: (new_grid, action_taken)
        """
        r, c = -1, -1
        # Find 0 position
        for i in range(3):
            for j in range(3):
                if grid[i][j] == 0:
                    r, c = i, j
                    break
        
        neighbors = []
        # Action indicates where the empty tile moves
        moves = [(-1, 0, "UP"), (1, 0, "DOWN"), (0, -1, "LEFT"), (0, 1, "RIGHT")]
        
        for dr, dc, action in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                # Convert grid to mutable list of lists
                temp = [list(row) for row in grid]
                # Swap values
                temp[r][c], temp[nr][nc] = temp[nr][nc], temp[r][c]
                new_grid = tuple(tuple(row) for row in temp)
                neighbors.append((new_grid, action))
                
        return neighbors

    def init_search(self):
        """
        Prepares the Frontier, Explored set, parent map, and stats to begin A* search.
        """
        self.counter = 0
        self.frontier = []
        self.explored = set()
        self.parent_map = {self.current_state: (None, None)}
        
        g = 0
        h = self.get_misplaced_tiles(self.current_state)
        f = g + h
        
        heapq.heappush(self.frontier, (f, self.counter, g, h, self.current_state))
        self.state = "searching"
        self.nodes_expanded = 0
        self.max_frontier_size = 1
        self.solution_path = []
        self.path_cost = 0

    def step_search(self):
        """
        Performs ONE expansion step of the A* search.
        Returns a log dictionary of details for the UI console, or None if finished.
        """
        if self.state != "searching":
            return None
            
        if not self.frontier:
            self.state = "unsolvable"
            return {
                "status": "failed",
                "log": "Frontier is empty. No solution exists for this configuration!"
            }
            
        # Pop the lowest f value node
        f, cnt, g, h, curr_grid = heapq.heappop(self.frontier)
        
        # Skip if already explored
        while curr_grid in self.explored:
            if not self.frontier:
                self.state = "unsolvable"
                return {
                    "status": "failed",
                    "log": "Frontier is empty. No solution exists!"
                }
            f, cnt, g, h, curr_grid = heapq.heappop(self.frontier)
            
        # Mark as explored
        self.explored.add(curr_grid)
        self.nodes_expanded += 1
        self.current_state = curr_grid
        
        # Build logs before potential return
        flat_curr = [val for row in curr_grid for val in row]
        log_entry = {
            "status": "searching",
            "node_explored": {
                "grid": curr_grid,
                "flat": flat_curr,
                "f": f,
                "g": g,
                "h": h
            },
            "frontier_size": len(self.frontier),
            "explored_size": len(self.explored),
            # Extract first few elements in frontier for display
            "frontier_sample": [(item[0], item[2], item[3], [v for r in item[4] for v in r]) for item in sorted(self.frontier)[:5]],
            "explored_sample": [[v for r in item for v in r] for item in list(self.explored)[-5:]]
        }
        
        # Goal check
        if curr_grid == self.goal_state:
            self.state = "solved"
            self.reconstruct_path()
            log_entry["status"] = "solved"
            log_entry["solution_length"] = len(self.solution_path) - 1
            log_entry["log"] = f"🎯 Success! Goal state reached.\nPath length: {len(self.solution_path) - 1} moves.\nNodes expanded: {self.nodes_expanded}"
            return log_entry

        # Expand neighbors
        for neighbor_grid, action in self.get_neighbors(curr_grid):
            if neighbor_grid not in self.explored:
                # With consistent heuristic (like misplaced tiles), the first time we discover
                # a node, it is not necessarily the optimal path if we use normal A*, but in 8-puzzle
                # with Hamming, h(n) is consistent, so first pop is optimal. We check if we have 
                # a better path (smaller g) if we have reached it before, or just register it if not.
                g_new = g + 1
                h_new = self.get_misplaced_tiles(neighbor_grid)
                f_new = g_new + h_new
                
                # Check if this state was seen before
                is_better = False
                if neighbor_grid not in self.parent_map:
                    is_better = True
                
                if is_better:
                    self.parent_map[neighbor_grid] = (curr_grid, action)
                    self.counter += 1
                    heapq.heappush(self.frontier, (f_new, self.counter, g_new, h_new, neighbor_grid))
                    
        self.max_frontier_size = max(self.max_frontier_size, len(self.frontier))
        return log_entry

    def reconstruct_path(self):
        """
        Traces back the parent pointers from the goal state to the start state.
        Stores the sequence of grids in self.solution_path.
        """
        path = []
        curr = self.goal_state
        while curr is not None:
            path.append(curr)
            curr, action = self.parent_map.get(curr, (None, None))
        path.reverse()
        self.solution_path = path
        self.path_cost = len(path) - 1

    def solve_all(self):
        """
        Executes the entire search instantly in the background.
        """
        self.init_search()
        while self.state == "searching":
            self.step_search()
        return self.solution_path


class EightPuzzleApp:
    """
    View / Controller: Builds a high-fidelity Tkinter GUI for the 8-puzzle.
    Uses custom styles, dynamic colored blocks, step searching, and console logs.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver AI - Hamming A*")
        self.root.geometry("1080x720")
        self.root.configure(bg="#1E1E2E")
        
        # Initialize Engine Model
        self.engine = EightPuzzle()
        self.initial_custom_state = self.engine.current_state
        
        # Playback & Search variables
        self.playback_index = 0
        self.auto_solve_running = False
        self.auto_search_running = False
        self.animation_speed = 300 # milliseconds
        
        # Setup UI layout
        self.setup_styles()
        self.build_ui()
        
        # Initial draw
        self.update_board_view()
        self.log_to_console("🚀 8-Puzzle Simulator initialized.\nGoal state is [1, 2, 3, 4, 5, 6, 7, 8, 0].\nClick 'Random' to generate a solvable start, or manually click tiles in idle mode to shift them.\n")

    def setup_styles(self):
        # Configure fonts and general ttk styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Custom button and scrollbar colors to match premium dark theme
        self.style.configure(".", bg="#1E1E2E", foreground="#CDD6F4")
        self.style.configure("TFrame", background="#1E1E2E")
        
        self.style.configure("TButton", 
                             background="#313244", 
                             foreground="#CDD6F4", 
                             font=("Segoe UI", 10, "bold"),
                             borderwidth=0,
                             focusthickness=0,
                             padding=6)
        self.style.map("TButton", 
                       background=[("active", "#45475A"), ("disabled", "#181825")],
                       foreground=[("disabled", "#585B70")])
                       
        self.style.configure("Primary.TButton", 
                             background="#89B4FA", 
                             foreground="#11111B",
                             font=("Segoe UI", 10, "bold"))
        self.style.map("Primary.TButton", 
                       background=[("active", "#B4BEFE"), ("disabled", "#181825")])

        self.style.configure("Accent.TButton", 
                             background="#A6E3A1", 
                             foreground="#11111B",
                             font=("Segoe UI", 10, "bold"))
        self.style.map("Accent.TButton", 
                       background=[("active", "#94E2D5"), ("disabled", "#181825")])

    def build_ui(self):
        # Main layout: Left sidebar/board, Right console/stats
        self.main_pane = tk.PanedWindow(self.root, bg="#1E1E2E", bd=0, sashwidth=4, sashpad=2)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        # ----------------- LEFT PANE: Grid and Controls -----------------
        self.left_frame = tk.Frame(self.main_pane, bg="#1E1E2E", padx=15, pady=15)
        self.main_pane.add(self.left_frame, minsize=420)

        # Header Title
        title_label = tk.Label(self.left_frame, text="8-PUZZLE SOLVER (A*)", bg="#1E1E2E", fg="#89B4FA", font=("Segoe UI", 18, "bold"))
        title_label.pack(anchor="w", pady=(0, 2))
        
        subtitle_label = tk.Label(self.left_frame, text="Heuristic: Misplaced Tiles (Hamming Distance)", bg="#1E1E2E", fg="#A6ADC8", font=("Segoe UI", 10, "italic"))
        subtitle_label.pack(anchor="w", pady=(0, 15))

        # The 3x3 Tile Grid Canvas Frame
        self.grid_frame = tk.Frame(self.left_frame, bg="#11111B", bd=3, relief="flat", highlightbackground="#313244", highlightthickness=2)
        self.grid_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Grid layout configure
        for r in range(3):
            self.grid_frame.rowconfigure(r, weight=1, uniform="equal")
            self.grid_frame.columnconfigure(r, weight=1, uniform="equal")
            
        self.tile_buttons = [[None for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                btn = tk.Button(self.grid_frame, 
                                text="", 
                                font=("Segoe UI", 28, "bold"),
                                bd=0, 
                                relief="flat",
                                activebackground="#45475A",
                                command=lambda row=r, col=c: self.on_tile_clicked(row, col))
                btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
                self.tile_buttons[r][c] = btn

        # Left control buttons panel
        self.controls_frame = tk.Frame(self.left_frame, bg="#1E1E2E", pady=10)
        self.controls_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Control Buttons row 1
        self.btn_random = ttk.Button(self.controls_frame, text="🎲 Random State", style="TButton", command=self.on_random)
        self.btn_random.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        
        self.btn_solve_instantly = ttk.Button(self.controls_frame, text="⚡ Solve Instantly", style="Primary.TButton", command=self.on_solve_instantly)
        self.btn_solve_instantly.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        # Control Buttons row 2
        self.btn_step_search = ttk.Button(self.controls_frame, text="🔍 Step Search", style="TButton", command=self.on_step_search)
        self.btn_step_search.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        
        self.btn_auto_search = ttk.Button(self.controls_frame, text="▶️ Auto Search Steps", style="TButton", command=self.toggle_auto_search)
        self.btn_auto_search.grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        # Playback controls row (initially hidden or disabled until solved)
        self.playback_frame = tk.LabelFrame(self.controls_frame, text="Playback controls (Solution found)", bg="#1E1E2E", fg="#A6ADC8", font=("Segoe UI", 9), padx=5, pady=5)
        self.playback_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        self.playback_frame.columnconfigure((0,1,2,3), weight=1)
        
        self.btn_prev = ttk.Button(self.playback_frame, text="⏪ Prev", style="TButton", state="disabled", command=self.on_prev_step)
        self.btn_prev.grid(row=0, column=0, padx=2, pady=2)
        
        self.btn_play = ttk.Button(self.playback_frame, text="▶️ Play", style="Accent.TButton", state="disabled", command=self.toggle_playback)
        self.btn_play.grid(row=0, column=1, padx=2, pady=2)
        
        self.btn_next = ttk.Button(self.playback_frame, text="Next ⏩", style="TButton", state="disabled", command=self.on_next_step)
        self.btn_next.grid(row=0, column=2, padx=2, pady=2)
        
        self.btn_reset = ttk.Button(self.playback_frame, text="🔄 Reset", style="TButton", state="disabled", command=self.on_reset)
        self.btn_reset.grid(row=0, column=3, padx=2, pady=2)

        self.controls_frame.columnconfigure((0, 1), weight=1)

        # Speed slider
        speed_frame = tk.Frame(self.left_frame, bg="#1E1E2E", pady=5)
        speed_frame.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(speed_frame, text="Playback/Search delay (ms):", bg="#1E1E2E", fg="#A6ADC8", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.speed_scale = tk.Scale(speed_frame, from_=50, to=1500, orient=tk.HORIZONTAL, bg="#1E1E2E", fg="#CDD6F4", highlightthickness=0, troughcolor="#313244", activebackground="#89B4FA")
        self.speed_scale.set(self.animation_speed)
        self.speed_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # ----------------- RIGHT PANE: Stats and Terminal Logs -----------------
        self.right_frame = tk.Frame(self.main_pane, bg="#1E1E2E", padx=15, pady=15)
        self.main_pane.add(self.right_frame, minsize=520)

        # Statistics Dashboard
        stats_header = tk.Label(self.right_frame, text="ALGORITHM STATISTICS", bg="#1E1E2E", fg="#F9E2AF", font=("Segoe UI", 12, "bold"))
        stats_header.pack(anchor="w", pady=(0, 8))

        self.stats_container = tk.Frame(self.right_frame, bg="#252538", bd=1, relief="flat", highlightbackground="#313244", highlightthickness=1)
        self.stats_container.pack(fill=tk.X, pady=(0, 15))
        
        # Grid system inside stats
        for i in range(2):
            self.stats_container.rowconfigure(i, weight=1)
            self.stats_container.columnconfigure(i, weight=1)
            
        self.stat_nodes = self.create_stat_card(self.stats_container, "Nodes Expanded (Tập mở rộng)", "0", 0, 0)
        self.stat_frontier = self.create_stat_card(self.stats_container, "Max Frontier (Biên lớn nhất)", "0", 0, 1)
        self.stat_depth = self.create_stat_card(self.stats_container, "Solution Depth (Số bước giải)", "0", 1, 0)
        self.stat_status = self.create_stat_card(self.stats_container, "Search Status (Trạng thái)", "IDLE", 1, 1, color="#89B4FA")

        # Scrolling terminal log
        log_header = tk.Label(self.right_frame, text="A* SEARCH CONSOLE TERMINAL", bg="#1E1E2E", fg="#CDD6F4", font=("Segoe UI", 12, "bold"))
        log_header.pack(anchor="w", pady=(0, 8))

        self.console_frame = tk.Frame(self.right_frame, bg="#11111B", bd=2, relief="flat")
        self.console_frame.pack(fill=tk.BOTH, expand=True)

        self.console_text = tk.Text(self.console_frame, 
                                    bg="#11111B", 
                                    fg="#A6E3A1", 
                                    insertbackground="#CDD6F4", 
                                    font=("Consolas", 9),
                                    bd=0,
                                    padx=10,
                                    pady=10)
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.console_frame, orient=tk.VERTICAL, command=self.console_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console_text.configure(yscrollcommand=self.scrollbar.set)
        
        # Console configurations
        self.console_text.configure(state="disabled")

    def create_stat_card(self, parent, title, value, r, c, color="#F9E2AF"):
        card = tk.Frame(parent, bg="#252538", padx=10, pady=8, bd=1, relief="flat")
        card.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
        
        lbl_title = tk.Label(card, text=title, bg="#252538", fg="#A6ADC8", font=("Segoe UI", 8))
        lbl_title.pack(anchor="w")
        
        lbl_val = tk.Label(card, text=value, bg="#252538", fg=color, font=("Segoe UI", 14, "bold"))
        lbl_val.pack(anchor="w", pady=(2, 0))
        return lbl_val

    def log_to_console(self, text):
        self.console_text.configure(state="normal")
        self.console_text.insert(tk.END, text + "\n")
        self.console_text.see(tk.END)
        self.console_text.configure(state="disabled")
        print(text) # Also output to terminal for console logs requested by the user

    def clear_console(self):
        self.console_text.configure(state="normal")
        self.console_text.delete(1.0, tk.END)
        self.console_text.configure(state="disabled")

    def update_board_view(self):
        # Redraw tiles based on self.engine.current_state
        grid = self.engine.current_state
        goal = self.engine.goal_state
        
        for r in range(3):
            for c in range(3):
                val = grid[r][c]
                btn = self.tile_buttons[r][c]
                
                if val == 0:
                    btn.configure(text="", bg="#11111B", activebackground="#11111B", state="disabled")
                else:
                    # Styling: green border/glow if correctly placed, amber/white otherwise
                    is_correct = (val == goal[r][c])
                    bg_color = "#313244" # Normal slate tile
                    fg_color = "#CDD6F4" # Off-white text
                    
                    if is_correct:
                        bg_color = "#253825" # Soft green background
                        fg_color = "#A6E3A1" # Neon green text
                    else:
                        bg_color = "#383125" # Soft amber background
                        fg_color = "#F9E2AF" # Neon amber text
                        
                    btn.configure(text=str(val), 
                                  bg=bg_color, 
                                  fg=fg_color, 
                                  activebackground="#45475A", 
                                  state="normal")

    def on_tile_clicked(self, r, c):
        # In manual mode (idle state), clicking a tile adjacent to 0 swaps it with 0.
        if self.engine.state not in ("idle", "solved"):
            return
            
        grid = [list(row) for row in self.engine.current_state]
        
        # Find 0
        zr, zc = -1, -1
        for i in range(3):
            for j in range(3):
                if grid[i][j] == 0:
                    zr, zc = i, j
                    break
                    
        # Check adjacency
        if abs(zr - r) + abs(zc - c) == 1:
            # Swap
            grid[zr][zc], grid[r][c] = grid[r][c], grid[zr][zc]
            self.engine.current_state = tuple(tuple(row) for row in grid)
            self.initial_custom_state = self.engine.current_state
            
            # Check solvability
            solvable = self.engine.is_solvable(self.engine.current_state)
            
            self.update_board_view()
            self.clear_search_state()
            
            if solvable:
                self.stat_status.configure(text="IDLE", fg="#89B4FA")
            else:
                self.stat_status.configure(text="UNSOLVABLE", fg="#F38BA8")
                self.log_to_console("⚠️ WARNING: The custom state is mathematically UNSOLVABLE!\nTry swapping adjacent tiles to make it solvable.\n")

    def on_random(self):
        self.stop_all_threads()
        self.clear_console()
        
        grid = self.engine.generate_random_solvable()
        self.engine = EightPuzzle(grid)
        self.initial_custom_state = grid
        
        self.playback_index = 0
        self.update_board_view()
        self.clear_search_state()
        
        flat = [val for row in grid for val in row]
        self.log_to_console(f"🎲 Generated new random solvable initial state:\n   {flat[:3]}\n   {flat[3:6]}\n   {flat[6:9]}\nInversions: {self.engine.count_inversions(grid)} (Even -> Solvable)\n")

    def clear_search_state(self):
        self.engine.state = "idle"
        self.engine.solution_path = []
        self.engine.nodes_expanded = 0
        self.engine.max_frontier_size = 0
        
        # Update UI stats
        self.stat_nodes.configure(text="0")
        self.stat_frontier.configure(text="0")
        self.stat_depth.configure(text="0")
        self.stat_status.configure(text="IDLE", fg="#89B4FA")
        
        # Disable playback buttons
        self.btn_prev.configure(state="disabled")
        self.btn_play.configure(state="disabled")
        self.btn_next.configure(state="disabled")
        self.btn_reset.configure(state="disabled")

    def stop_all_threads(self):
        self.auto_solve_running = False
        self.auto_search_running = False
        self.btn_play.configure(text="▶️ Play")
        self.btn_auto_search.configure(text="▶️ Auto Search Steps")

    def on_solve_instantly(self):
        self.stop_all_threads()
        self.clear_console()
        
        # Solvability check
        if not self.engine.is_solvable(self.initial_custom_state):
            messagebox.showerror("Error", "The current puzzle is mathematically unsolvable!")
            return
            
        self.log_to_console("⚡ Solving instantly with A* (Misplaced Tiles Heuristic)...")
        start_time = time.time()
        
        # Setup engine from original custom start
        self.engine = EightPuzzle(self.initial_custom_state)
        self.engine.init_search()
        
        # Keep stepping until solved
        logs = []
        while self.engine.state == "searching":
            step_log = self.engine.step_search()
            if step_log:
                logs.append(step_log)
                
        elapsed = time.time() - start_time
        
        if self.engine.state == "solved":
            # Output full summary and final steps
            self.log_to_console(f"🎯 Solved in {elapsed:.4f} seconds!")
            self.log_to_console(f"   Nodes expanded: {self.engine.nodes_expanded}")
            self.log_to_console(f"   Max Frontier size: {self.engine.max_frontier_size}")
            self.log_to_console(f"   Optimal solution path depth: {self.engine.path_cost} moves.")
            
            # Print a concise representation of the moves in console
            self.log_to_console("\n📋 SOLUTION PATH TRANSITIONS:")
            for i, step_state in enumerate(self.engine.solution_path):
                flat = [v for r in step_state for v in r]
                self.log_to_console(f"   Step {i}: {flat}")
            
            # Print last step's search details
            if logs:
                last = logs[-1]
                self.log_to_console(f"\n🔬 LAST EXPLORED STATE DETAIL:")
                self.log_to_console(f"   - Current Node: {last['node_explored']['flat']} (f={last['node_explored']['f']}, g={last['node_explored']['g']}, h={last['node_explored']['h']})")
                self.log_to_console(f"   - Frontier Size: {last['frontier_size']}")
                self.log_to_console(f"   - Explored Size: {last['explored_size']}")
                
            # Update stats
            self.stat_nodes.configure(text=str(self.engine.nodes_expanded))
            self.stat_frontier.configure(text=str(self.engine.max_frontier_size))
            self.stat_depth.configure(text=str(self.engine.path_cost))
            self.stat_status.configure(text="SOLVED", fg="#A6E3A1")
            
            # Enable playback
            self.playback_index = 0
            self.engine.current_state = self.engine.solution_path[0]
            self.update_board_view()
            
            self.btn_prev.configure(state="normal")
            self.btn_play.configure(state="normal")
            self.btn_next.configure(state="normal")
            self.btn_reset.configure(state="normal")
        else:
            self.log_to_console("❌ Search failed. Unsolvable configuration.")
            self.stat_status.configure(text="FAILED", fg="#F38BA8")

    def on_step_search(self):
        self.stop_all_threads()
        
        # Solvability check
        if not self.engine.is_solvable(self.initial_custom_state):
            messagebox.showerror("Error", "The current puzzle is mathematically unsolvable!")
            return
            
        # Initialize if not already searching
        if self.engine.state != "searching" and self.engine.state != "solved":
            self.clear_console()
            self.log_to_console("🔍 Initializing step-by-step search...")
            self.engine = EightPuzzle(self.initial_custom_state)
            self.engine.init_search()
            self.stat_status.configure(text="SEARCHING", fg="#F9E2AF")
            
        if self.engine.state == "searching":
            step_log = self.engine.step_search()
            if step_log:
                self.render_search_step_log(step_log)
                self.update_board_view()
                
                # Update stats
                self.stat_nodes.configure(text=str(self.engine.nodes_expanded))
                self.stat_frontier.configure(text=str(self.engine.max_frontier_size))
                self.stat_depth.configure(text=str(len(self.engine.explored)))
                
                if self.engine.state == "solved":
                    self.stat_status.configure(text="SOLVED", fg="#A6E3A1")
                    self.stat_depth.configure(text=str(self.engine.path_cost))
                    self.playback_index = 0
                    
                    self.btn_prev.configure(state="normal")
                    self.btn_play.configure(state="normal")
                    self.btn_next.configure(state="normal")
                    self.btn_reset.configure(state="normal")
                    self.log_to_console("\n🎉 Success! You solved the puzzle manually step-by-step. Playback is now enabled.")

    def render_search_step_log(self, step_log):
        node = step_log["node_explored"]
        self.log_to_console("-" * 65)
        self.log_to_console(f"📍 Expanding Node: {node['flat']}")
        self.log_to_console(f"   Evaluations:  f(n) = {node['f']}   [g(n) = {node['g']}, h(n) = {node['h']} (Misplaced)]")
        self.log_to_console(f"   Frontier Size: {step_log['frontier_size']}   |   Explored Set Size: {step_log['explored_size']}")
        
        # Display Frontier
        self.log_to_console("   Frontier Open Queue (Priority Order, top 5):")
        if not step_log["frontier_sample"]:
            self.log_to_console("     [Empty]")
        for item in step_log["frontier_sample"]:
            self.log_to_console(f"     • f={item[0]} (g={item[1]}, h={item[2]}) -> State: {item[3]}")
            
        # Display Explored Set Sample
        self.log_to_console("   Explored Set (Closed List, last 5 expanded):")
        if not step_log["explored_sample"]:
            self.log_to_console("     [Empty]")
        for item in step_log["explored_sample"]:
            self.log_to_console(f"     ✓ State: {item}")
        self.log_to_console("")

    def toggle_auto_search(self):
        if self.auto_search_running:
            self.auto_search_running = False
            self.btn_auto_search.configure(text="▶️ Auto Search Steps")
        else:
            if not self.engine.is_solvable(self.initial_custom_state):
                messagebox.showerror("Error", "The current puzzle is mathematically unsolvable!")
                return
            self.stop_all_threads()
            self.auto_search_running = True
            self.btn_auto_search.configure(text="⏸️ Pause Search")
            
            # Start automatic stepping thread
            threading.Thread(target=self.auto_search_loop, daemon=True).start()

    def auto_search_loop(self):
        # Initialize search if needed
        if self.engine.state != "searching" and self.engine.state != "solved":
            self.root.after(0, self.clear_console)
            self.root.after(0, lambda: self.log_to_console("🔍 Initializing search loop..."))
            self.engine = EightPuzzle(self.initial_custom_state)
            self.engine.init_search()
            self.root.after(0, lambda: self.stat_status.configure(text="SEARCHING", fg="#F9E2AF"))
            time.sleep(0.1)

        while self.auto_search_running and self.engine.state == "searching":
            # Retrieve speed value safely from main thread
            delay = self.speed_scale.get() / 1000.0
            
            # Perform search step on UI thread via sync execution
            def run_step():
                if self.engine.state == "searching":
                    step_log = self.engine.step_search()
                    if step_log:
                        self.render_search_step_log(step_log)
                        self.update_board_view()
                        
                        # Update stats
                        self.stat_nodes.configure(text=str(self.engine.nodes_expanded))
                        self.stat_frontier.configure(text=str(self.engine.max_frontier_size))
                        self.stat_depth.configure(text=str(len(self.engine.explored)))
                        
                        if self.engine.state == "solved":
                            self.stat_status.configure(text="SOLVED", fg="#A6E3A1")
                            self.stat_depth.configure(text=str(self.engine.path_cost))
                            self.playback_index = 0
                            
                            self.btn_prev.configure(state="normal")
                            self.btn_play.configure(state="normal")
                            self.btn_next.configure(state="normal")
                            self.btn_reset.configure(state="normal")
                            self.log_to_console("\n🎉 Success! Auto-Search found the solution path. Playback is now enabled.")
                            self.stop_all_threads()
            
            self.root.after(0, run_step)
            time.sleep(delay)
            
        if self.engine.state != "searching" and self.auto_search_running:
            self.root.after(0, self.stop_all_threads)

    # ----------------- PLAYBACK MECHANISMS -----------------
    def on_prev_step(self):
        self.stop_all_threads()
        if self.playback_index > 0:
            self.playback_index -= 1
            self.engine.current_state = self.engine.solution_path[self.playback_index]
            self.update_board_view()
            self.log_to_console(f"⏪ Playback step {self.playback_index}/{self.engine.path_cost}")

    def on_next_step(self):
        self.stop_all_threads()
        if self.playback_index < len(self.engine.solution_path) - 1:
            self.playback_index += 1
            self.engine.current_state = self.engine.solution_path[self.playback_index]
            self.update_board_view()
            self.log_to_console(f"⏩ Playback step {self.playback_index}/{self.engine.path_cost}")

    def on_reset(self):
        self.stop_all_threads()
        self.playback_index = 0
        self.engine.current_state = self.engine.solution_path[0]
        self.update_board_view()
        self.log_to_console("🔄 Playback reset to starting state.")

    def toggle_playback(self):
        if self.auto_solve_running:
            self.auto_solve_running = False
            self.btn_play.configure(text="▶️ Play")
        else:
            self.stop_all_threads()
            self.auto_solve_running = True
            self.btn_play.configure(text="⏸️ Pause")
            threading.Thread(target=self.playback_loop, daemon=True).start()

    def playback_loop(self):
        while self.auto_solve_running:
            if self.playback_index >= len(self.engine.solution_path) - 1:
                # Loop completed, reset to start or stop
                self.root.after(0, self.stop_all_threads)
                self.root.after(0, lambda: self.log_to_console("🏁 Playback finished!"))
                break
                
            delay = self.speed_scale.get() / 1000.0
            
            def run_play():
                if self.playback_index < len(self.engine.solution_path) - 1:
                    self.playback_index += 1
                    self.engine.current_state = self.engine.solution_path[self.playback_index]
                    self.update_board_view()
                    self.log_to_console(f"▶️ Auto-step {self.playback_index}/{self.engine.path_cost}")
                    
            self.root.after(0, run_play)
            time.sleep(delay)


if __name__ == "__main__":
    root = tk.Tk()
    app = EightPuzzleApp(root)
    root.mainloop()
