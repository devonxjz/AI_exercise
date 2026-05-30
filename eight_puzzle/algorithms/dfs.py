from eight_puzzle.solver import BaseSolver
from eight_puzzle.board import PuzzleBoard

class DFSSolver(BaseSolver):
    """
    Adapter implementing Depth-First Search (DFS).
    Uses a LIFO stack. Does not guarantee optimal path.
    """
    def init_search(self):
        super().init_search()
        self.frontier = [(self.start_state, 0)]  # Stack of (state, depth)
        self.frontier_set = {self.start_state}

    def step_search(self):
        if self.state != "searching":
            return None
            
        if not self.frontier:
            self.state = "unsolvable"
            return {
                "status": "failed",
                "log": "Frontier is empty. No solution exists!"
            }
            
        curr_grid, depth = self.frontier.pop()
        self.frontier_set.remove(curr_grid)
        self.explored.add(curr_grid)
        self.explored_sample.append(curr_grid)
        self.nodes_expanded += 1
        self.current_state = curr_grid
        
        flat_curr = [val for row in curr_grid for val in row]
        
        # O(1) g-cost lookup
        g = depth
                
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
            # Show top elements of stack
            "frontier_sample": [(0, 0, 0, [v for r in item[0] for v in r]) for item in reversed(self.frontier[-5:])],
            "explored_sample": [[v for r in item for v in r] for item in self.explored_sample]
        }
        
        if curr_grid == self.goal_state:
            self.state = "solved"
            self.reconstruct_path()
            log_entry["status"] = "solved"
            log_entry["solution_length"] = len(self.solution_path) - 1
            log_entry["log"] = f"🎯 Success! Goal state reached via DFS.\nPath length: {len(self.solution_path) - 1} moves.\nNodes expanded: {self.nodes_expanded}"
            return log_entry
            
        # Expand neighbors only if depth < 50
        if depth < 50:
            board = PuzzleBoard(curr_grid)
            for neighbor_grid, action in board.get_neighbors():
                if neighbor_grid not in self.explored and neighbor_grid not in self.frontier_set:
                    self.parent_map[neighbor_grid] = (curr_grid, action)
                    self.g_map[neighbor_grid] = depth + 1
                    self.frontier.append((neighbor_grid, depth + 1))
                    self.frontier_set.add(neighbor_grid)
                
        self.max_frontier_size = max(self.max_frontier_size, len(self.frontier))
        return log_entry
