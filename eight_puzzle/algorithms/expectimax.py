from eight_puzzle.solver import BaseSolver
from eight_puzzle.board import PuzzleBoard

class ExpectimaxSolver(BaseSolver):
    """
    Adapter implementing Expectimax search for the 8-puzzle.
    At each step, MAX player looks ahead to choose a move that maximizes the utility
    under the assumption that a hypothetical CHANCE player chooses moves with equal probability.
    """
    def __init__(self, start_state, goal_state=PuzzleBoard.GOAL_STATE, depth=3, max_steps=100):
        super().__init__(start_state, goal_state)
        self.search_depth = depth
        self.max_steps = max_steps
        self.steps_taken = 0
        self.path_history = []

    def init_search(self):
        super().init_search()
        self.steps_taken = 0
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
        h_val = self.get_manhattan_distance(curr_grid)

        # Log entry for current state before moving
        log_entry = {
            "status": "searching",
            "node_explored": {
                "grid": curr_grid,
                "flat": flat_curr,
                "g": self.steps_taken,
                "h": h_val,
                "f": self.steps_taken + h_val
            },
            "frontier_size": 0,
            "explored_size": len(self.explored),
            "frontier_sample": [],
            "explored_sample": [[v for r in item for v in r] for item in self.explored_sample]
        }

        if curr_grid == self.goal_state:
            self.state = "solved"
            self.reconstruct_path()
            log_entry["status"] = "solved"
            log_entry["solution_length"] = len(self.solution_path) - 1
            log_entry["log"] = f"🎯 Success! Goal state reached via Expectimax.\nPath length: {len(self.solution_path) - 1} moves.\nSteps taken: {self.steps_taken}\nNodes expanded: {self.nodes_expanded}"
            return log_entry

        if self.steps_taken >= self.max_steps:
            self.state = "unsolvable"
            log_entry["status"] = "failed"
            log_entry["log"] = f"❌ Expectimax failed to reach goal within {self.max_steps} steps."
            return log_entry

        # Generate neighbor states (moves) and run expectimax search
        board = PuzzleBoard(curr_grid)
        neighbors = board.get_neighbors()
        if not neighbors:
            self.state = "unsolvable"
            log_entry["status"] = "failed"
            log_entry["log"] = "❌ No moves available from current state."
            return log_entry

        best_value = -float('inf')
        best_state = None
        best_action = None
        frontier_sample = []

        for next_grid, action in neighbors:
            val = self.chancev(next_grid, depth=1)
            frontier_sample.append((val, self.steps_taken + 1, self.get_manhattan_distance(next_grid), [v for r in next_grid for v in r]))
            if val > best_value:
                best_value = val
                best_state = next_grid
                best_action = action

        # Sort frontier_sample descending by score
        frontier_sample.sort(key=lambda x: x[0], reverse=True)
        log_entry["frontier_size"] = len(neighbors)
        log_entry["frontier_sample"] = frontier_sample
        self.max_frontier_size = max(self.max_frontier_size, len(neighbors))

        if best_state is None:
            self.state = "unsolvable"
            log_entry["status"] = "failed"
            log_entry["log"] = "❌ Expectimax search returned no valid moves."
            return log_entry

        # Move to next state
        self.parent_map[best_state] = (curr_grid, best_action)
        self.explored.add(best_state)
        self.explored_sample.append(best_state)
        self.steps_taken += 1
        self.current_state = best_state
        self.path_history.append(best_state)
        self.g_map[best_state] = self.steps_taken

        log_entry["log"] = f"🤖 Expectimax at step {self.steps_taken} chose move {best_action} with expected value {best_value:.2f}."
        return log_entry

    def reconstruct_path(self):
        self.solution_path = self.path_history
        self.path_cost = len(self.solution_path) - 1

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

    def maxv(self, state, depth):
        self.nodes_expanded += 1
        if state == self.goal_state:
            return 10000 - depth
        if depth >= self.search_depth:
            return -self.get_manhattan_distance(state)

        board = PuzzleBoard(state)
        neighbors = board.get_neighbors()
        if not neighbors:
            return -10000

        val = -float('inf')
        for next_grid, _ in neighbors:
            val = max(val, self.chancev(next_grid, depth + 1))
        return val

    def chancev(self, state, depth):
        self.nodes_expanded += 1
        if state == self.goal_state:
            return 10000 - depth
        if depth >= self.search_depth:
            return -self.get_manhattan_distance(state)

        board = PuzzleBoard(state)
        neighbors = board.get_neighbors()
        if not neighbors:
            return 0

        total_val = 0.0
        for next_grid, _ in neighbors:
            total_val += self.maxv(next_grid, depth + 1)
        return total_val / len(neighbors)
