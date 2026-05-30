from collections import deque
from eight_puzzle.solver import BaseSolver
from eight_puzzle.board import PuzzleBoard

class BFSSolver(BaseSolver):
    """
    Adapter implementing Breadth-First Search (BFS).
    Uses a standard FIFO queue. Guarantees shortest path for unweighted steps.
    """
    def init_search(self):
        super().init_search()
        self.frontier = deque([self.start_state])
        self.frontier_set = {self.start_state}  # For O(1) membership check

    def step_search(self):
        if self.state != "searching":
            return None
            
        if not self.frontier:
            self.state = "unsolvable"
            return {
                "status": "failed",
                "log": "Frontier is empty. No solution exists!"
            }
            
        curr_grid = self.frontier.popleft()
        self.frontier_set.remove(curr_grid)
        self.explored.add(curr_grid)
        self.explored_sample.append(curr_grid)
        self.nodes_expanded += 1
        self.current_state = curr_grid
        
        flat_curr = [val for row in curr_grid for val in row]
        
        # O(1) g-cost lookup
        g = self.g_map.get(curr_grid, 0)
                
        # O(1) slice of first 5 elements in deque without list copy
        frontier_sample_nodes = []
        for i, item in enumerate(self.frontier):
            if i >= 5:
                break
            frontier_sample_nodes.append(item)
                
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
            "frontier_sample": [(0, 0, 0, [v for r in item for v in r]) for item in frontier_sample_nodes],
            "explored_sample": [[v for r in item for v in r] for item in self.explored_sample]
        }
        
        if curr_grid == self.goal_state:
            self.state = "solved"
            self.reconstruct_path()
            log_entry["status"] = "solved"
            log_entry["solution_length"] = len(self.solution_path) - 1
            log_entry["log"] = f"🎯 Success! Goal state reached via BFS.\nPath length: {len(self.solution_path) - 1} moves.\nNodes expanded: {self.nodes_expanded}"
            return log_entry
            
        # Expand neighbors
        board = PuzzleBoard(curr_grid)
        for neighbor_grid, action in board.get_neighbors():
            if neighbor_grid not in self.explored and neighbor_grid not in self.frontier_set:
                self.parent_map[neighbor_grid] = (curr_grid, action)
                self.g_map[neighbor_grid] = g + 1
                self.frontier.append(neighbor_grid)
                self.frontier_set.add(neighbor_grid)
                
        self.max_frontier_size = max(self.max_frontier_size, len(self.frontier))
        return log_entry
