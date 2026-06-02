from eight_puzzle.solver import BaseSolver
from eight_puzzle.board import PuzzleBoard

class LocalBeamSearchSolver(BaseSolver):
    """
    Adapter implementing Local Beam Search.
    Keeps track of k states simultaneously (beam width k).
    At each step, all successors of the k states are generated and evaluated.
    The k best unique, unexplored successors are selected for the next step.
    """
    def __init__(self, start_state, goal_state=PuzzleBoard.GOAL_STATE, k=3):
        super().__init__(start_state, goal_state)
        self.k = k
        self.beam = []

    def get_manhattan_distance(self, grid):
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
        self.beam = [self.start_state]
        self.frontier = list(self.beam)
        self.max_frontier_size = len(self.frontier)

    def _build_log_entry(self, curr_grid, g_curr, h_curr, flat_curr):
        # Format the frontier sample with the elements currently in the beam
        frontier_sample = []
        for state in self.beam:
            h_val = self.get_manhattan_distance(state)
            g_val = self.g_map.get(state, 0)
            flat_state = [v for r in state for v in r]
            frontier_sample.append((h_val, g_val, h_val, flat_state))

        return {
            "status": "searching",
            "node_explored": {
                "grid": curr_grid,
                "flat": flat_curr,
                "g": g_curr,
                "h": h_curr,
                "f": h_curr
            },
            "frontier_size": len(self.beam),
            "explored_size": len(self.explored),
            "frontier_sample": frontier_sample[:5], # show top 5 in beam
            "explored_sample": [[v for r in item for v in r] for item in self.explored_sample]
        }

    def step_search(self):
        if self.state != "searching":
            return None

        # Check if goal is already in the beam (e.g. at start or after select)
        for state in self.beam:
            if state == self.goal_state:
                self.current_state = self.goal_state
                self.state = "solved"
                self.reconstruct_path()
                flat_curr = [val for row in self.goal_state for val in row]
                log_entry = self._build_log_entry(self.goal_state, self.g_map.get(self.goal_state, 0), 0, flat_curr)
                log_entry["status"] = "solved"
                log_entry["solution_length"] = len(self.solution_path) - 1
                log_entry["log"] = f"🎯 Success! Goal state reached via Local Beam Search.\nPath length: {len(self.solution_path) - 1} moves.\nNodes expanded: {self.nodes_expanded}"
                return log_entry

        # Pick the best state in the current beam as the representative node for logging
        best_state = min(self.beam, key=self.get_manhattan_distance)
        self.current_state = best_state
        h_curr = self.get_manhattan_distance(best_state)
        g_curr = self.g_map.get(best_state, 0)
        flat_curr = [val for row in best_state for val in row]

        log_entry = self._build_log_entry(best_state, g_curr, h_curr, flat_curr)

        # Mark all beam states as explored
        for state in self.beam:
            if state not in self.explored:
                self.explored.add(state)
                self.explored_sample.append(state)
                self.nodes_expanded += 1

        # Generate successors for all states in the current beam
        successors = []
        for state in self.beam:
            board = PuzzleBoard(state)
            g_parent = self.g_map.get(state, 0)
            for neighbor_grid, action in board.get_neighbors():
                # If we haven't seen this neighbor or found a cheaper path, record parent
                if neighbor_grid not in self.parent_map:
                    self.parent_map[neighbor_grid] = (state, action)
                    self.g_map[neighbor_grid] = g_parent + 1
                
                # Check if this neighbor is the goal
                if neighbor_grid == self.goal_state:
                    self.current_state = self.goal_state
                    self.state = "solved"
                    self.reconstruct_path()
                    log_entry["status"] = "solved"
                    log_entry["solution_length"] = len(self.solution_path) - 1
                    log_entry["log"] = f"🎯 Success! Goal state reached via Local Beam Search.\nPath length: {len(self.solution_path) - 1} moves.\nNodes expanded: {self.nodes_expanded}"
                    return log_entry

                if neighbor_grid not in self.explored:
                    successors.append(neighbor_grid)

        if not successors:
            self.state = "unsolvable"
            log_entry["status"] = "failed"
            log_entry["log"] = f"❌ Search failed. No unexplored successors available."
            return log_entry

        # Deduplicate successors
        unique_successors = list(set(successors))

        # Sort successors by heuristic value (Manhattan Distance)
        unique_successors.sort(key=self.get_manhattan_distance)

        # Select top k successors to form the new beam
        self.beam = unique_successors[:self.k]
        self.frontier = list(self.beam)
        self.max_frontier_size = max(self.max_frontier_size, len(self.frontier))

        # Set current state to the best state in the new beam
        self.current_state = self.beam[0]

        return log_entry
