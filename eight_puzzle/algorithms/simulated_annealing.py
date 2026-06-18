import random
import math
from collections import deque
from eight_puzzle.solver import BaseSolver
from eight_puzzle.board import PuzzleBoard

class SimulatedAnnealingSolver(BaseSolver):
    """
    Adapter implementing Simulated Annealing (Local Search).
    Uses Manhattan Distance as the heuristic h(n).
    
    Algorithm (from lecture pseudocode):
        SimulatedAnnealing(start, goal):
            current state = start
            T = T0
            while T > Tmin:
                if current state == goal: return current state
                next state = RandomNeighbor(current state)
                Δ = h(next state) - h(current state)
                if Δ < 0:
                    current = next
                else:
                    p = exp(-Δ / T)
                    if Random(0,1) < p:
                        current = next state
                T = α * T
            return current state
    
    Unlike pure hill climbing, SA accepts worse moves with probability exp(-Δ/T),
    allowing it to escape local optima. As temperature T decreases, the algorithm
    becomes more greedy and less likely to accept worse moves.
    
    Auto-restart: When temperature cools below Tmin without finding goal,
    the algorithm restarts from the start state with fresh temperature
    (up to max_restarts times) to increase success rate.
    
    Path tracking uses parent_map with cycle-safe reconstruction
    (maximum depth limit to prevent infinite loops).
    """
    def __init__(self, start_state, goal_state=PuzzleBoard.GOAL_STATE, seed=None,
                 initial_temp=100.0, min_temp=0.001, cooling_rate=0.995,
                 max_restarts=50):
        super().__init__(start_state, goal_state)
        # Instantiate a local Random instance if seed is provided, otherwise use global random
        self.rng = random.Random(seed) if seed is not None else random
        # SA parameters
        self.initial_temp = initial_temp
        self.min_temp = min_temp
        self.cooling_rate = cooling_rate  # α in pseudocode
        self.temperature = initial_temp   # T in pseudocode
        self.max_restarts = max_restarts
        self.restart_count = 0

    def get_manhattan_distance(self, grid):
        """Calculates Manhattan Distance heuristic h(n)."""
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
        self.temperature = self.initial_temp
        self.restart_count = 0
        # Use parent_map for path but reset per restart
        self.parent_map = {self.start_state: (None, None)}
        self.g_map = {self.start_state: 0}

    def _restart_from_start(self):
        """Reset temperature and current state to start for a fresh SA run."""
        self.restart_count += 1
        self.temperature = self.initial_temp
        self.current_state = self.start_state
        self.frontier = [self.start_state]
        # Clear parent_map to avoid cycles from previous run
        self.parent_map = {self.start_state: (None, None)}
        self.g_map = {self.start_state: 0}

    def _reconstruct_path_safe(self):
        """
        Cycle-safe path reconstruction from goal back to start.
        Uses a visited set to detect and break cycles.
        """
        path = []
        curr = self.goal_state
        visited = set()
        while curr is not None and curr not in visited:
            visited.add(curr)
            path.append(curr)
            parent_entry = self.parent_map.get(curr, (None, None))
            curr = parent_entry[0]
        path.reverse()
        self.solution_path = path
        self.path_cost = len(path) - 1

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

        # Check if current state is goal
        if curr_grid == self.goal_state:
            self.state = "solved"
            self._reconstruct_path_safe()
            log_entry["status"] = "solved"
            log_entry["solution_length"] = self.path_cost
            log_entry["log"] = (
                f"🎯 Success! Goal state reached via Simulated Annealing.\n"
                f"Path length: {self.path_cost} moves.\n"
                f"Nodes expanded: {self.nodes_expanded}\n"
                f"Restarts used: {self.restart_count}/{self.max_restarts}"
            )
            return log_entry

        # Check temperature stopping condition: T > Tmin
        if self.temperature <= self.min_temp:
            if self.restart_count < self.max_restarts:
                # Auto-restart with fresh temperature
                self._restart_from_start()
                log_entry["log"] = (
                    f"🔄 Temperature cooled below Tmin. Restarting ({self.restart_count}/{self.max_restarts})..."
                )
                return log_entry
            else:
                # All restarts exhausted
                self.state = "unsolvable"
                log_entry["status"] = "failed"
                log_entry["log"] = (
                    f"❌ Temperature cooled to {self.temperature:.6f} (below Tmin={self.min_temp}).\n"
                    f"All {self.max_restarts} restarts exhausted.\n"
                    f"Simulated Annealing stopped at state {flat_curr} (h={h_curr}).\n"
                    f"Nodes expanded: {self.nodes_expanded}"
                )
                return log_entry

        # Get random neighbor: next state = RandomNeighbor(current state)
        board = PuzzleBoard(curr_grid)
        neighbors = board.get_neighbors()
        next_grid, action = self.rng.choice(neighbors)
        h_next = self.get_manhattan_distance(next_grid)

        # Δ = h(next state) - h(current state)
        delta = h_next - h_curr

        accept = False
        if delta < 0:
            # Better state: always accept
            accept = True
        else:
            # Worse or equal state: accept with probability p = exp(-Δ / T)
            p = math.exp(-delta / self.temperature)
            if self.rng.random() < p:
                accept = True

        if accept:
            # Only update parent if next_grid not already in parent_map
            # This prevents cycles in the reconstruction chain
            if next_grid not in self.parent_map:
                self.parent_map[next_grid] = (curr_grid, action)
            self.g_map[next_grid] = g_curr + 1
            self.current_state = next_grid
            self.frontier = [next_grid]

        # Cool down: T = α * T
        self.temperature *= self.cooling_rate
        self.max_frontier_size = max(self.max_frontier_size, len(self.frontier))

        return log_entry
