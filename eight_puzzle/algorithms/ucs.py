import heapq
from eight_puzzle.solver import BaseSolver
from eight_puzzle.board import PuzzleBoard

class UCSSolver(BaseSolver):
    """
    Adapter implementing Uniform Cost Search (UCS) / Dijkstra.
    Uses a Priority Queue sorted by path cost g.
    Since step costs are equal (1), UCS acts identically to BFS but operates via Priority Queue.
    """
    def init_search(self):
        super().init_search()
        self.counter = 0
        # Frontier contains elements: (g_cost, tie_break_counter, state_grid)
        self.frontier = [(0, self.counter, self.start_state)]

    def step_search(self):
        if self.state != "searching":
            return None
            
        if not self.frontier:
            self.state = "unsolvable"
            return {
                "status": "failed",
                "log": "Frontier is empty. No solution exists!"
            }
            
        g, cnt, curr_grid = heapq.heappop(self.frontier)
        
        # Lazy decrease-key check: skip if we already found a better path
        while curr_grid in self.explored or g > self.g_map.get(curr_grid, float('inf')):
            if not self.frontier:
                self.state = "unsolvable"
                return {
                    "status": "failed",
                    "log": "Frontier is empty. No solution exists!"
                }
            g, cnt, curr_grid = heapq.heappop(self.frontier)
            
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
                "h": 0,
                "f": g
            },
            "frontier_size": len(self.frontier),
            "explored_size": len(self.explored),
            "frontier_sample": [(item[0], item[0], 0, [v for r in item[2] for v in r]) for item in frontier_sample_nodes],
            "explored_sample": [[v for r in item for v in r] for item in self.explored_sample]
        }
        
        if curr_grid == self.goal_state:
            self.state = "solved"
            self.reconstruct_path()
            log_entry["status"] = "solved"
            log_entry["solution_length"] = len(self.solution_path) - 1
            log_entry["log"] = f"🎯 Success! Goal state reached via UCS.\nPath length: {len(self.solution_path) - 1} moves.\nNodes expanded: {self.nodes_expanded}"
            return log_entry
            
        # Expand neighbors
        board = PuzzleBoard(curr_grid)
        for neighbor_grid, action in board.get_neighbors():
            if neighbor_grid not in self.explored:
                g_new = g + 1
                
                # Check if this new path is strictly better than any we have recorded so far
                if g_new < self.g_map.get(neighbor_grid, float('inf')):
                    self.parent_map[neighbor_grid] = (curr_grid, action)
                    self.g_map[neighbor_grid] = g_new
                    self.counter += 1
                    heapq.heappush(self.frontier, (g_new, self.counter, neighbor_grid))
                    
        self.max_frontier_size = max(self.max_frontier_size, len(self.frontier))
        return log_entry
