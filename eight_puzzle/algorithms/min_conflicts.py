import random
from eight_puzzle.solver import BaseSolver
from eight_puzzle.board import PuzzleBoard

class MinConflictsSolver(BaseSolver):
    """
    Adapter implementing Min-Conflicts Local Search.
    Starts at the start state, select a conflicting tile adjacent to the blank tile,
    and swap it with the blank tile to minimize misplaced tiles.
    """
    def __init__(self, start_state, goal_state=PuzzleBoard.GOAL_STATE, max_steps=1000, seed=42):
        super().__init__(start_state, goal_state)
        self.max_steps = max_steps
        self.seed = seed
        self.rng = random.Random(seed)
        self.steps_taken = 0
        self.path_history = []

    def init_search(self):
        super().init_search()
        self.steps_taken = 0
        self.rng = random.Random(self.seed)
        self.current_state = self.start_state
        self.explored.add(self.start_state)
        self.explored_sample.append(self.start_state)
        self.path_history = [self.start_state]
        self.max_frontier_size = 1

    def step_search(self):
        if self.state != "searching":
            return None

        curr_grid = self.current_state
        flat_curr = [val for row in curr_grid for val in row]
        h_val = self.count_conflicts(curr_grid)

        # Log entry for current state before moving
        log_entry = {
            "status": "searching",
            "node_explored": {
                "grid": curr_grid,
                "flat": flat_curr,
                "g": self.steps_taken,
                "h": h_val,
                "f": h_val
            },
            "frontier_size": 1,
            "explored_size": len(self.explored),
            "frontier_sample": [(h_val, self.steps_taken, h_val, flat_curr)],
            "explored_sample": [[v for r in item for v in r] for item in self.explored_sample]
        }

        if curr_grid == self.goal_state:
            self.state = "solved"
            self.reconstruct_path()
            log_entry["status"] = "solved"
            log_entry["solution_length"] = len(self.solution_path) - 1
            log_entry["log"] = f"🎯 Success! Goal state reached via Min-Conflicts.\nPath length: {len(self.solution_path) - 1} moves.\nSteps taken: {self.steps_taken}"
            return log_entry

        if self.steps_taken >= self.max_steps:
            self.state = "unsolvable"
            log_entry["status"] = "failed"
            log_entry["log"] = f"❌ Min-Conflicts failed to converge within {self.max_steps} steps."
            return log_entry

        # Generate neighbor states (moves)
        board = PuzzleBoard(curr_grid)
        neighbors = board.get_neighbors()

        # Identify coordinates of the blank tile 0 in curr_grid
        zr, zc = -1, -1
        for r in range(3):
            for c in range(3):
                if curr_grid[r][c] == 0:
                    zr, zc = r, c
                    break

        conflicting_neighbors = []
        all_candidates = []

        for next_grid, action in neighbors:
            # Find which tile was swapped into (zr, zc)
            val_swapped = next_grid[zr][zc]
            orig_r, orig_c = -1, -1
            for r in range(3):
                for c in range(3):
                    if curr_grid[r][c] == val_swapped:
                        orig_r, orig_c = r, c
                        break
            
            is_in_conflict = (val_swapped != self.goal_state[orig_r][orig_c])
            conflicts_count = self.count_conflicts(next_grid)
            
            cand_info = (conflicts_count, next_grid, action)
            all_candidates.append(cand_info)
            if is_in_conflict:
                conflicting_neighbors.append(cand_info)

        candidates = conflicting_neighbors if conflicting_neighbors else all_candidates

        # Find the minimum conflicts count among these candidates
        min_conflicts = min(cand[0] for cand in candidates)
        
        # Filter candidates that achieve this minimum conflicts count
        best_candidates = [cand for cand in candidates if cand[0] == min_conflicts]

        # Randomly choose one from the best candidates
        chosen_conflicts, next_state, chosen_action = self.rng.choice(best_candidates)

        # Move to next state
        self.parent_map[next_state] = (curr_grid, chosen_action)
        self.explored.add(next_state)
        self.explored_sample.append(next_state)
        self.nodes_expanded += 1
        self.steps_taken += 1
        self.current_state = next_state
        self.path_history.append(next_state)

        self.g_map[next_state] = self.steps_taken

        return log_entry

    def reconstruct_path(self):
        self.solution_path = self.path_history
        self.path_cost = len(self.solution_path) - 1

    def count_conflicts(self, grid):
        """
        Count conflicts: number of misplaced tiles (non-zero tiles not in goal position).
        """
        conflicts = 0
        for r in range(3):
            for c in range(3):
                val = grid[r][c]
                if val != 0 and val != self.goal_state[r][c]:
                    conflicts += 1
        return conflicts
