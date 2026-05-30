import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading

from eight_puzzle.board import PuzzleBoard
from eight_puzzle.algorithms import SOLVER_REGISTRY, ALGORITHM_THEMES

class EightPuzzleApp:
    """
    View / Controller: Builds a high-fidelity Tkinter GUI for the 8-puzzle.
    Uses Catppuccin Mocha theme, dynamic colored elements, step-by-step playback,
    and a unified console log interface.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle AI Solver - Multi-Algorithm Console")
        self.root.geometry("1120x760")
        self.root.configure(bg="#1E1E2E")
        
        # Current Board State (starts with a random solvable configuration)
        self.initial_custom_state = PuzzleBoard.generate_random_solvable()
        
        # Selected Algorithm
        self.algo_list = list(SOLVER_REGISTRY.keys())
        self.selected_algo_name = "A* Search (Manhattan Distance)"
        
        # Initialize Engine with selected algorithm
        self.engine = SOLVER_REGISTRY[self.selected_algo_name](self.initial_custom_state)
        
        # Playback & Threading variables
        self.playback_index = 0
        self.auto_solve_running = False
        self.auto_search_running = False
        self.animation_speed = 300  # milliseconds
        
        # Setup UI
        self.setup_styles()
        self.build_ui()
        
        # Initial render and welcome log
        self.update_board_view()
        self.on_algo_changed()
        self.log_to_console("🚀 8-Puzzle Simulator initialized.\nGoal state is [1, 2, 3, 4, 5, 6, 7, 8, 0].\nSelect an algorithm and click '🎲 Random State' or click tiles to modify state.\n")

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Base Dark Theme styling
        self.style.configure(".", bg="#1E1E2E", foreground="#CDD6F4")
        self.style.configure("TFrame", background="#1E1E2E")
        self.style.configure("LabelFrame", background="#1E1E2E", foreground="#A6ADC8")
        
        # Clean button styling
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
                       
        # Primary Action Button
        self.style.configure("Primary.TButton", 
                             background="#89B4FA", 
                             foreground="#11111B",
                             font=("Segoe UI", 10, "bold"))
        self.style.map("Primary.TButton", 
                       background=[("active", "#B4BEFE"), ("disabled", "#181825")])

        # Playback Active Button
        self.style.configure("Accent.TButton", 
                             background="#A6E3A1", 
                             foreground="#11111B",
                             font=("Segoe UI", 10, "bold"))
        self.style.map("Accent.TButton", 
                       background=[("active", "#94E2D5"), ("disabled", "#181825")])

        # ComboBox Styling
        self.style.configure("TCombobox", 
                             fieldbackground="#313244", 
                             background="#45475A", 
                             foreground="#CDD6F4", 
                             arrowcolor="#CDD6F4")
        self.root.option_add('*TCombobox*Listbox.background', '#313244')
        self.root.option_add('*TCombobox*Listbox.foreground', '#CDD6F4')
        self.root.option_add('*TCombobox*Listbox.selectBackground', '#89B4FA')
        self.root.option_add('*TCombobox*Listbox.selectForeground', '#11111B')

    def build_ui(self):
        # Main layout splitter
        self.main_pane = tk.PanedWindow(self.root, bg="#1E1E2E", bd=0, sashwidth=4, sashpad=2)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        # ----------------- LEFT PANE: Grid, Selector and Controls -----------------
        self.left_frame = tk.Frame(self.main_pane, bg="#1E1E2E", padx=15, pady=15)
        self.main_pane.add(self.left_frame, minsize=460)

        # Title Block
        self.title_label = tk.Label(self.left_frame, text="8-PUZZLE SOLVER AI", bg="#1E1E2E", fg="#89B4FA", font=("Segoe UI", 18, "bold"))
        self.title_label.pack(anchor="w", pady=(0, 2))
        
        self.subtitle_label = tk.Label(self.left_frame, text="Heuristic: Misplaced Tiles (Hamming Distance)", bg="#1E1E2E", fg="#A6ADC8", font=("Segoe UI", 10, "italic"))
        self.subtitle_label.pack(anchor="w", pady=(0, 10))

        # Algorithm Selection Frame
        selector_frame = tk.LabelFrame(self.left_frame, text=" Select Algorithm (Chọn thuật toán) ", bg="#1E1E2E", fg="#A6ADC8", font=("Segoe UI", 9, "bold"), padx=10, pady=8)
        selector_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(selector_frame, text="Algorithm:", bg="#1E1E2E", fg="#CDD6F4", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.algo_combobox = ttk.Combobox(selector_frame, values=self.algo_list, state="readonly", width=35, style="TCombobox")
        self.algo_combobox.set(self.selected_algo_name)
        self.algo_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.algo_combobox.bind("<<ComboboxSelected>>", self.on_algo_changed)

        # 3x3 Tile Grid Canvas Frame
        self.grid_frame = tk.Frame(self.left_frame, bg="#11111B", bd=3, relief="flat", highlightbackground="#313244", highlightthickness=2)
        self.grid_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
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

        # Playback controls frame
        self.playback_frame = tk.LabelFrame(self.controls_frame, text=" Playback controls (Sau khi giải xong) ", bg="#1E1E2E", fg="#A6ADC8", font=("Segoe UI", 9), padx=5, pady=5)
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
        self.main_pane.add(self.right_frame, minsize=540)

        # Statistics Dashboard
        stats_header = tk.Label(self.right_frame, text="ALGORITHM STATISTICS", bg="#1E1E2E", fg="#F9E2AF", font=("Segoe UI", 12, "bold"))
        stats_header.pack(anchor="w", pady=(0, 8))

        self.stats_container = tk.Frame(self.right_frame, bg="#252538", bd=1, relief="flat", highlightbackground="#313244", highlightthickness=1)
        self.stats_container.pack(fill=tk.X, pady=(0, 15))
        
        for i in range(2):
            self.stats_container.rowconfigure(i, weight=1)
            self.stats_container.columnconfigure(i, weight=1)
            
        self.stat_nodes = self.create_stat_card(self.stats_container, "Nodes Expanded (Số nút duyệt)", "0", 0, 0)
        self.stat_frontier = self.create_stat_card(self.stats_container, "Max Frontier (Biên hàng đợi)", "0", 0, 1)
        self.stat_depth = self.create_stat_card(self.stats_container, "Solution Depth / Path Cost", "0", 1, 0)
        self.stat_status = self.create_stat_card(self.stats_container, "Search Status (Trạng thái)", "IDLE", 1, 1, color="#89B4FA")

        # Scrolling terminal log
        log_header = tk.Label(self.right_frame, text="SEARCH CONSOLE TERMINAL", bg="#1E1E2E", fg="#CDD6F4", font=("Segoe UI", 12, "bold"))
        log_header.pack(anchor="w", pady=(0, 8))

        self.console_frame = tk.Frame(self.right_frame, bg="#11111B", bd=2, relief="flat")
        self.console_frame.pack(fill=tk.BOTH, expand=True)

        # Console Text Area
        self.console_text = tk.Text(self.console_frame, 
                                    bg="#11111B", 
                                    fg="#A6E3A1", 
                                    insertbackground="#CDD6F4", 
                                    font=("Consolas", 10),
                                    bd=0,
                                    padx=12,
                                    pady=12)
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.console_frame, orient=tk.VERTICAL, command=self.console_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console_text.configure(yscrollcommand=self.scrollbar.set)
        
        self.console_text.configure(state="disabled")

    def create_stat_card(self, parent, title, value, r, c, color="#F9E2AF"):
        card = tk.Frame(parent, bg="#252538", padx=12, pady=10, bd=1, relief="flat")
        card.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
        
        lbl_title = tk.Label(card, text=title, bg="#252538", fg="#A6ADC8", font=("Segoe UI", 9))
        lbl_title.pack(anchor="w")
        
        lbl_val = tk.Label(card, text=value, bg="#252538", fg=color, font=("Segoe UI", 15, "bold"))
        lbl_val.pack(anchor="w", pady=(3, 0))
        return lbl_val

    def log_to_console(self, text):
        self.console_text.configure(state="normal")
        self.console_text.insert(tk.END, text + "\n")
        self.console_text.see(tk.END)
        self.console_text.configure(state="disabled")
        try:
            print(text)
        except Exception:
            try:
                # Fallback to printing with replaced characters
                import sys
                encoding = sys.stdout.encoding or 'utf-8'
                print(text.encode(encoding, errors='replace').decode(encoding))
            except Exception:
                pass

    def clear_console(self):
        self.console_text.configure(state="normal")
        self.console_text.delete(1.0, tk.END)
        self.console_text.configure(state="disabled")

    def update_board_view(self):
        grid = self.engine.current_state
        goal = self.engine.goal_state
        
        for r in range(3):
            for c in range(3):
                val = grid[r][c]
                btn = self.tile_buttons[r][c]
                
                if val == 0:
                    btn.configure(text="", bg="#11111B", activebackground="#11111B", state="disabled")
                else:
                    # Highlight correct positions
                    is_correct = (val == goal[r][c])
                    
                    if is_correct:
                        bg_color = "#253825"  # Soft green
                        fg_color = "#A6E3A1"  # Bright green
                    else:
                        bg_color = "#383125"  # Soft amber
                        fg_color = "#F9E2AF"  # Bright amber
                        
                    btn.configure(text=str(val), 
                                  bg=bg_color, 
                                  fg=fg_color, 
                                  activebackground="#45475A", 
                                  state="normal")

    def on_algo_changed(self, event=None):
        self.stop_all_threads()
        self.selected_algo_name = self.algo_combobox.get()
        
        # Get theme configuration for active algorithm
        theme = ALGORITHM_THEMES.get(self.selected_algo_name, {
            "accent": "#CDD6F4",
            "accent_bg": "#313244",
            "description": "8-Puzzle Search solver"
        })
        
        # Update colors & fonts in UI dynamically based on algorithm theme
        self.title_label.configure(fg=theme["accent"])
        self.subtitle_label.configure(text=theme["description"])
        
        # Reconfigure console text color to match the selected algorithm accent
        self.console_text.configure(fg=theme["accent"])
        
        # Reset engine and clean state
        self.engine = SOLVER_REGISTRY[self.selected_algo_name](self.initial_custom_state)
        self.clear_search_state()
        self.update_board_view()
        self.clear_console()
        self.log_to_console(f"🔄 Switched algorithm to: {self.selected_algo_name}")
        self.log_to_console(f"Configured visual theme to {theme['accent']}.\n")

    def on_tile_clicked(self, r, c):
        if self.engine.state not in ("idle", "solved"):
            return
            
        grid = [list(row) for row in self.engine.current_state]
        
        # Find position of 0
        zr, zc = -1, -1
        for i in range(3):
            for j in range(3):
                if grid[i][j] == 0:
                    zr, zc = i, j
                    break
                    
        # Check adjacency to empty cell (0)
        if abs(zr - r) + abs(zc - c) == 1:
            grid[zr][zc], grid[r][c] = grid[r][c], grid[zr][zc]
            self.initial_custom_state = tuple(tuple(row) for row in grid)
            
            # Check solvability
            solvable = PuzzleBoard.is_solvable(self.initial_custom_state)
            
            # Recreate Solver engine
            self.engine = SOLVER_REGISTRY[self.selected_algo_name](self.initial_custom_state)
            
            self.update_board_view()
            self.clear_search_state()
            
            if solvable:
                self.stat_status.configure(text="IDLE", fg="#89B4FA")
            else:
                self.stat_status.configure(text="UNSOLVABLE", fg="#F38BA8")
                self.log_to_console("⚠️ WARNING: The custom state is mathematically UNSOLVABLE (odd inversion count)!\nSwap two adjacent numbers to fix it.\n")

    def on_random(self):
        self.stop_all_threads()
        self.clear_console()
        
        # Generate new random solvable grid
        grid = PuzzleBoard.generate_random_solvable()
        self.initial_custom_state = grid
        
        # Recreate engine
        self.engine = SOLVER_REGISTRY[self.selected_algo_name](self.initial_custom_state)
        
        self.playback_index = 0
        self.update_board_view()
        self.clear_search_state()
        
        flat = [val for row in grid for val in row]
        self.log_to_console(f"🎲 Generated random solvable start state:\n   {flat[:3]}\n   {flat[3:6]}\n   {flat[6:9]}\nInversions: {PuzzleBoard.count_inversions(grid)} (Even -> Solvable)\n")

    def clear_search_state(self):
        self.engine.state = "idle"
        self.engine.solution_path = []
        self.engine.nodes_expanded = 0
        self.engine.max_frontier_size = 0
        
        # Update UI labels
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

    def set_controls_state(self, state):
        self.btn_random.configure(state=state)
        self.btn_solve_instantly.configure(state=state)
        self.btn_step_search.configure(state=state)
        self.btn_auto_search.configure(state=state)
        self.algo_combobox.configure(state=state)

    def on_solve_instantly(self):
        self.stop_all_threads()
        self.clear_console()
        
        if not PuzzleBoard.is_solvable(self.initial_custom_state):
            messagebox.showerror("Error", "The current puzzle is mathematically unsolvable!")
            return
            
        self.log_to_console(f"⚡ Solving instantly using {self.selected_algo_name}...")
        self.stat_status.configure(text="SEARCHING", fg="#F9E2AF")
        
        # Disable controls to prevent concurrent searches
        self.set_controls_state("disabled")
        
        # Start search in background thread
        threading.Thread(target=self.solve_instantly_background, daemon=True).start()

    def solve_instantly_background(self):
        start_time = time.time()
        
        # Re-initialize search
        self.engine = SOLVER_REGISTRY[self.selected_algo_name](self.initial_custom_state)
        self.engine.init_search()
        
        logs = []
        iterations = 0
        while self.engine.state == "searching":
            step_log = self.engine.step_search()
            if step_log:
                if len(logs) < 100:
                    logs.append(step_log)
                else:
                    # Keep memory overhead low by replacing the last log
                    logs[-1] = step_log
            
            iterations += 1
            if iterations % 1000 == 0:
                time.sleep(0.001)  # Yield CPU to the GUI main thread to keep it responsive
                
        elapsed = time.time() - start_time
        
        # Dispatch UI update back to main thread
        self.root.after(0, lambda: self.solve_instantly_ui_callback(elapsed, logs))

    def solve_instantly_ui_callback(self, elapsed, logs):
        # Enable controls back
        self.set_controls_state("normal")
        self.algo_combobox.configure(state="readonly")
        
        if self.engine.state == "solved":
            theme = ALGORITHM_THEMES.get(self.selected_algo_name, {"accent": "#A6E3A1"})
            
            self.log_to_console(f"🎯 Solved in {elapsed:.4f} seconds!")
            self.log_to_console(f"   Nodes expanded: {self.engine.nodes_expanded}")
            self.log_to_console(f"   Max Frontier size: {self.engine.max_frontier_size}")
            self.log_to_console(f"   Solution path depth: {self.engine.path_cost} moves.")
            
            self.log_to_console("\n📋 SOLUTION PATH TRANSITIONS:")
            for i, step_state in enumerate(self.engine.solution_path):
                flat = [v for r in step_state for v in r]
                self.log_to_console(f"   Step {i}: {flat}")
            
            if logs:
                last = logs[-1]
                node = last['node_explored']
                self.log_to_console(f"\n🔬 LAST EXPLORED STATE DETAIL:")
                self.log_to_console(f"   - Current Node: {node['flat']} (g={node['g']}, h={node['h']}, f={node['f']})")
                self.log_to_console(f"   - Frontier Size: {last['frontier_size']}")
                self.log_to_console(f"   - Explored Size: {last['explored_size']}")
                
            # Update stats UI
            self.stat_nodes.configure(text=str(self.engine.nodes_expanded))
            self.stat_frontier.configure(text=str(self.engine.max_frontier_size))
            self.stat_depth.configure(text=str(self.engine.path_cost))
            self.stat_status.configure(text="SOLVED", fg=theme["accent"])
            
            # Enable playback controls
            self.playback_index = 0
            self.engine.current_state = self.engine.solution_path[0]
            self.update_board_view()
            
            self.btn_prev.configure(state="normal")
            self.btn_play.configure(state="normal")
            self.btn_next.configure(state="normal")
            self.btn_reset.configure(state="normal")
        else:
            self.log_to_console("❌ Search failed / unsolvable state.")
            self.stat_status.configure(text="FAILED", fg="#F38BA8")

    def on_step_search(self):
        self.stop_all_threads()
        
        if not PuzzleBoard.is_solvable(self.initial_custom_state):
            messagebox.showerror("Error", "The current puzzle is mathematically unsolvable!")
            return
            
        # Re-initialize search if idle
        if self.engine.state not in ("searching", "solved"):
            self.clear_console()
            self.log_to_console(f"🔍 Initializing step-by-step search with {self.selected_algo_name}...")
            self.engine = SOLVER_REGISTRY[self.selected_algo_name](self.initial_custom_state)
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
                    theme = ALGORITHM_THEMES.get(self.selected_algo_name, {"accent": "#A6E3A1"})
                    self.stat_status.configure(text="SOLVED", fg=theme["accent"])
                    self.stat_depth.configure(text=str(self.engine.path_cost))
                    self.playback_index = 0
                    
                    self.btn_prev.configure(state="normal")
                    self.btn_play.configure(state="normal")
                    self.btn_next.configure(state="normal")
                    self.btn_reset.configure(state="normal")
                    self.log_to_console("\n🎉 Success! You solved the puzzle manually. Playback is now enabled.")

    def render_search_step_log(self, step_log):
        node = step_log["node_explored"]
        self.log_to_console("-" * 65)
        self.log_to_console(f"📍 Expanding Node: {node['flat']}")
        self.log_to_console(f"   Evaluations:  g = {node['g']}   |   h = {node['h']}   |   f = {node['f']}")
        self.log_to_console(f"   Frontier Queue Size: {step_log['frontier_size']}   |   Explored Set: {step_log['explored_size']}")
        
        # Display sample from frontier
        self.log_to_console("   Frontier Open Queue (sample top 5):")
        if not step_log["frontier_sample"]:
            self.log_to_console("     [Empty]")
        for item in step_log["frontier_sample"]:
            # item = (f, g, h, state_flat) or similar layout
            self.log_to_console(f"     • state: {item[3]} (g={item[1]}, h={item[2]}, f={item[0]})")
            
        # Display sample from explored set
        self.log_to_console("   Explored Set (sample last 5):")
        if not step_log["explored_sample"]:
            self.log_to_console("     [Empty]")
        for item in step_log["explored_sample"]:
            self.log_to_console(f"     ✓ state: {item}")
        self.log_to_console("")

    def toggle_auto_search(self):
        if self.auto_search_running:
            self.auto_search_running = False
            self.btn_auto_search.configure(text="▶️ Auto Search Steps")
        else:
            if not PuzzleBoard.is_solvable(self.initial_custom_state):
                messagebox.showerror("Error", "The current puzzle is mathematically unsolvable!")
                return
            self.stop_all_threads()
            self.auto_search_running = True
            self.btn_auto_search.configure(text="⏸️ Pause Search")
            
            threading.Thread(target=self.auto_search_loop, daemon=True).start()

    def auto_search_loop(self):
        if self.engine.state not in ("searching", "solved"):
            self.root.after(0, self.clear_console)
            self.root.after(0, lambda: self.log_to_console(f"🔍 Initializing auto search with {self.selected_algo_name}..."))
            self.engine = SOLVER_REGISTRY[self.selected_algo_name](self.initial_custom_state)
            self.engine.init_search()
            self.root.after(0, lambda: self.stat_status.configure(text="SEARCHING", fg="#F9E2AF"))
            time.sleep(0.1)

        while self.auto_search_running and self.engine.state == "searching":
            delay = self.speed_scale.get() / 1000.0
            
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
                            theme = ALGORITHM_THEMES.get(self.selected_algo_name, {"accent": "#A6E3A1"})
                            self.stat_status.configure(text="SOLVED", fg=theme["accent"])
                            self.stat_depth.configure(text=str(self.engine.path_cost))
                            self.playback_index = 0
                            
                            self.btn_prev.configure(state="normal")
                            self.btn_play.configure(state="normal")
                            self.btn_next.configure(state="normal")
                            self.btn_reset.configure(state="normal")
                            self.log_to_console("\n🎉 Success! Auto-Search found solution path. Playback is now enabled.")
                            self.stop_all_threads()
            
            self.root.after(0, run_step)
            time.sleep(delay)
            
        if self.engine.state != "searching" and self.auto_search_running:
            self.root.after(0, self.stop_all_threads)

    # ----------------- PLAYBACK -----------------
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
