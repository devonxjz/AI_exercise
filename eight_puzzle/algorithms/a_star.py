import heapq
from eight_puzzle.solver import BaseSolver
from eight_puzzle.board import PuzzleBoard

class AStarSolver(BaseSolver):
    """
    Adapter implementing A* Search.
    Uses Manhattan Distance as heuristic h(n).
    Uses a Priority Queue sorted by f = g + h.
    """
    def get_manhattan_distance(self, grid):
        """
        Heuristic h(n): Manhattan Distance (Sum of absolute vertical and horizontal distances
        of each tile from its goal position).
        """
        dist = 0
        goal_pos = {
            1: (0, 0), 2: (0, 1), 3: (0, 2),
            4: (1, 0), 5: (1, 1), 6: (1, 2),
            7: (2, 0), 8: (2, 1)
        }
        for r in range(3):
            for c in range(3):
                val = grid[r][c]
                if val != 0:
                    tr, tc = goal_pos[val]
                    dist += abs(r - tr) + abs(c - tc)
        return dist

    def init_search(self):
        super().init_search()
        self.counter = 0
        h = self.get_manhattan_distance(self.start_state)
        # Frontier contains elements: (f_score, tie_break_counter, g_cost, h_cost, state_grid)
        self.frontier = [(h, self.counter, 0, h, self.start_state)]
        self.g_map = {self.start_state: 0}

    def step_search(self):
        if self.state != "searching":
            return None
            
        if not self.frontier:
            self.state = "unsolvable"
            return {
                "status": "failed",
                "log": "Frontier is empty. No solution exists!"
            }
            
        f, cnt, g, h, curr_grid = heapq.heappop(self.frontier)
        
        # Lazy decrease-key check: skip if we already found a better path
        while curr_grid in self.explored or g > self.g_map.get(curr_grid, float('inf')):
            if not self.frontier:
                self.state = "unsolvable"
                return {
                    "status": "failed",
                    "log": "Frontier is empty. No solution exists!"
                }
            f, cnt, g, h, curr_grid = heapq.heappop(self.frontier)
            
        self.explored.add(curr_grid)
        self.explored_sample.append(curr_grid)
        self.nodes_expanded += 1
        self.current_state = curr_grid
        
        flat_curr = [val for row in curr_grid for val in row]
        
        # O(1) slice of raw heap array for sampling
        frontier_sample_nodes = self.frontier[:5]
        
        log_entry = {
            "status": "searching",
            "node_explored": {
                "grid": curr_grid,
                "flat": flat_curr,
                "g": g,
                "h": h,
                "f": f
            },
            "frontier_size": len(self.frontier),
            "explored_size": len(self.explored),
            "frontier_sample": [(item[0], item[2], item[3], [v for r in item[4] for v in r]) for item in frontier_sample_nodes],
            "explored_sample": [[v for r in item for v in r] for item in self.explored_sample]
        }
        
        if curr_grid == self.goal_state:
            self.state = "solved"
            self.reconstruct_path()
            log_entry["status"] = "solved"
            log_entry["solution_length"] = len(self.solution_path) - 1
            log_entry["log"] = f"🎯 Success! Goal state reached via A*.\nPath length: {len(self.solution_path) - 1} moves.\nNodes expanded: {self.nodes_expanded}"
            return log_entry
            
        # Expand neighbors
        board = PuzzleBoard(curr_grid)
        for neighbor_grid, action in board.get_neighbors():
            if neighbor_grid not in self.explored:
                g_new = g + 1
                h_new = self.get_manhattan_distance(neighbor_grid)
                f_new = g_new + h_new
                
                # Check if this new path is strictly better than any we have recorded so far
                if g_new < self.g_map.get(neighbor_grid, float('inf')):
                    self.parent_map[neighbor_grid] = (curr_grid, action)
                    self.g_map[neighbor_grid] = g_new
                    self.counter += 1
                    heapq.heappush(self.frontier, (f_new, self.counter, g_new, h_new, neighbor_grid))
                    
        self.max_frontier_size = max(self.max_frontier_size, len(self.frontier))
        return log_entry
