from eight_puzzle.solver import BaseSolver
from eight_puzzle.board import PuzzleBoard

class HillClimbingSolver(BaseSolver):
    """
    Adapter implementing Hill Climbing (Local Search).
    Uses Manhattan Distance as the heuristic h(n).
    Moves to the best neighbor strictly minimizing h(n).
    Stops if no neighbor is strictly better than the current state (local optimum / peak / plateau).
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
        self.frontier = [self.start_state]

    def _build_log_entry(self, curr_grid, g_curr, h_curr, flat_curr):
        return {
            "status": "searching",
            "node_explored": {
                "grid": curr_grid,
                "flat": flat_curr,
                "g": g_curr,
                "h": h_curr,
                "f": h_curr
            },
            "frontier_size": len(self.frontier),
            "explored_size": len(self.explored),
            "frontier_sample": [(h_curr, g_curr, h_curr, flat_curr)],
            "explored_sample": [[v for r in item for v in r] for item in self.explored_sample]
        }

    def _find_best_neighbor(self, curr_grid):
        board = PuzzleBoard(curr_grid)
        best_neighbor = None
        best_h = float('inf')
        best_action = None

        # Deterministic tie-breaking (use first best neighbor generated)
        for neighbor_grid, action in board.get_neighbors():
            h_val = self.get_manhattan_distance(neighbor_grid)
            if h_val < best_h:
                best_h = h_val
                best_neighbor = neighbor_grid
                best_action = action
        return best_neighbor, best_h, best_action

    def step_search(self):
        if self.state != "searching":
            return None

        curr_grid = self.current_state
        self.explored.add(curr_grid)
        self.explored_sample.append(curr_grid)
        self.nodes_expanded += 1

        h_curr = self.get_manhattan_distance(curr_grid)
        g_curr = self.g_map.get(curr_grid, 0)
        flat_curr = [val for row in curr_grid for val in row]

        log_entry = self._build_log_entry(curr_grid, g_curr, h_curr, flat_curr)

        if curr_grid == self.goal_state:
            self.state = "solved"
            self.reconstruct_path()
            log_entry["status"] = "solved"
            log_entry["solution_length"] = len(self.solution_path) - 1
            log_entry["log"] = f"🎯 Success! Goal state reached via Hill Climbing.\nPath length: {len(self.solution_path) - 1} moves.\nNodes expanded: {self.nodes_expanded}"
            return log_entry

        best_neighbor, best_h, best_action = self._find_best_neighbor(curr_grid)

        # Steepest-ascent climbing condition: must strictly improve heuristic
        if best_neighbor is not None and best_h < h_curr:
            self.parent_map[best_neighbor] = (curr_grid, best_action)
            self.g_map[best_neighbor] = g_curr + 1
            self.current_state = best_neighbor
            self.frontier = [best_neighbor]
            self.max_frontier_size = max(self.max_frontier_size, len(self.frontier))
            return log_entry

        # Stuck in local optimum or plateau
        self.state = "unsolvable"
        log_entry["status"] = "failed"
        log_entry["log"] = f"❌ Stuck in local optimum at state {flat_curr} (h={h_curr}). No neighbor improves heuristic."
        return log_entry
