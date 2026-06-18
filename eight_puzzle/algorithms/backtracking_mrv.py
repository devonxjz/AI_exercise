from eight_puzzle.solver import BaseSolver
from eight_puzzle.board import PuzzleBoard

class BacktrackingMRVSolver(BaseSolver):
    """
    Adapter implementing Backtracking Search with MRV (Minimum-Remaining-Values) heuristic.
    """
    def init_search(self):
        super().init_search()
        # Stack of (state, depth, path_set)
        # We track path_set along the path to perform cycle detection.
        self.frontier = [(self.start_state, 0, frozenset([self.start_state]))]
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

        curr_grid, depth, path_set = self.frontier.pop()
        self.frontier_set.discard(curr_grid)
        self.explored.add(curr_grid)
        self.explored_sample.append(curr_grid)
        self.nodes_expanded += 1
        self.current_state = curr_grid

        flat_curr = [val for row in curr_grid for val in row]
        g = depth
        mrv_val = self.get_mrv_score(curr_grid)

        # Construct log_entry
        log_entry = {
            "status": "searching",
            "node_explored": {
                "grid": curr_grid,
                "flat": flat_curr,
                "g": g,
                "h": mrv_val,
                "f": g + mrv_val
            },
            "frontier_size": len(self.frontier),
            "explored_size": len(self.explored),
            "frontier_sample": [(g + mrv_val, g, mrv_val, [v for r in item[0] for v in r]) for item in reversed(self.frontier[-5:])],
            "explored_sample": [[v for r in item for v in r] for item in self.explored_sample]
        }

        if curr_grid == self.goal_state:
            self.state = "solved"
            self.reconstruct_path()
            log_entry["status"] = "solved"
            log_entry["solution_length"] = len(self.solution_path) - 1
            log_entry["log"] = f"🎯 Success! Goal state reached via Backtracking with MRV.\nPath length: {len(self.solution_path) - 1} moves.\nNodes expanded: {self.nodes_expanded}"
            return log_entry

        # Expand neighbors only if depth < 50
        if depth < 50:
            board = PuzzleBoard(curr_grid)
            neighbors = board.get_neighbors()
            
            # Sort neighbors based on MRV heuristic:
            # We want to prioritize the neighbor with the minimum remaining values (valid moves/neighbors).
            # So we sort neighbors by their number of valid moves/neighbors (ascending).
            # To push them onto the LIFO stack so the minimum is popped first, we push them in DESCENDING order of MRV score.
            neighbor_mrv_scores = []
            for n_grid, action in neighbors:
                if n_grid not in path_set:
                    mrv_score = self.get_mrv_score(n_grid)
                    neighbor_mrv_scores.append((mrv_score, n_grid, action))
            
            # Sort in descending order of MRV score so the minimum is at the end of list (pushed last, popped first)
            neighbor_mrv_scores.sort(key=lambda x: x[0], reverse=True)
            
            for mrv, n_grid, action in neighbor_mrv_scores:
                self.parent_map[n_grid] = (curr_grid, action)
                self.g_map[n_grid] = depth + 1
                self.frontier.append((n_grid, depth + 1, path_set.union([n_grid])))
                self.frontier_set.add(n_grid)

        self.max_frontier_size = max(self.max_frontier_size, len(self.frontier))
        return log_entry

    def get_mrv_score(self, grid):
        """
        Minimum-Remaining-Values score for a board state is defined as the number of valid moves from that state.
        Fewer moves = more constrained.
        """
        board = PuzzleBoard(grid)
        return len(board.get_neighbors())
