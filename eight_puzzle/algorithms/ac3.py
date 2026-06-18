from collections import deque
from eight_puzzle.solver import BaseSolver
from eight_puzzle.board import PuzzleBoard

class AC3Solver(BaseSolver):
    """
    Adapter implementing AC-3 (Arc Consistency 3) for the 8-puzzle.
    Formulates path finding as a CSP where variables are steps S_0, ..., S_D.
    """
    def __init__(self, start_state, goal_state=PuzzleBoard.GOAL_STATE, max_D=25):
        super().__init__(start_state, goal_state)
        self.max_D = max_D
        self.D = 0

    def init_search(self):
        super().init_search()
        self.D = self.get_manhattan_distance(self.start_state)
        self.current_state = self.start_state
        self.max_frontier_size = 1

    def step_search(self):
        if self.state != "searching":
            return None

        if self.start_state == self.goal_state:
            self.state = "solved"
            self.solution_path = [self.start_state]
            self.path_cost = 0
            return {
                "status": "solved",
                "node_explored": {
                    "grid": self.start_state,
                    "flat": [v for r in self.start_state for v in r],
                    "g": 0, "h": 0, "f": 0
                },
                "frontier_size": 0,
                "explored_size": 1,
                "frontier_sample": [],
                "explored_sample": [[v for r in self.start_state for v in r]],
                "log": "🎯 Success! Start state is already the Goal state."
            }

        if self.D > self.max_D:
            self.state = "unsolvable"
            return {
                "status": "failed",
                "log": f"❌ AC-3 search failed. Reached maximum depth limit D={self.max_D} without a solution."
            }

        # Step details to log to console
        depth = self.D
        self.nodes_expanded += 1
        
        # 1. Generate reachable states from start and goal (bidirectional BFS up to depth D)
        start_bfs = self.bfs_reachable(self.start_state, depth)
        goal_bfs = self.bfs_reachable(self.goal_state, depth)
        
        # Check if there is any intersection at depth
        intersection_found = False
        for i in range(depth + 1):
            if start_bfs[i].intersection(goal_bfs[depth - i]):
                intersection_found = True
                break

        if not intersection_found:
            log_entry = {
                "status": "searching",
                "node_explored": {
                    "grid": self.current_state,
                    "flat": [v for r in self.current_state for v in r],
                    "g": depth, "h": 0, "f": depth
                },
                "frontier_size": 1,
                "explored_size": len(self.explored),
                "frontier_sample": [],
                "explored_sample": [],
                "log": f"ℹ️ Checked depth D={depth}: No bidirectional intersection. Trying D={depth + 1}..."
            }
            self.D += 1
            return log_entry

        # 2. Define domains for variables S_0, ..., S_D
        # Domain(S_i) is the union of states at depth i from start and depth D-i from goal
        domains = {}
        for i in range(depth + 1):
            domains[i] = start_bfs[i].union(goal_bfs[depth - i])

        # Enforce boundary domains
        domains[0] = {self.start_state}
        domains[depth] = {self.goal_state}

        # Total size before AC-3
        total_initial_states = sum(len(domains[i]) for i in range(depth + 1))

        # 3. Build queue of arcs
        queue = deque()
        for i in range(depth):
            queue.append((i, i + 1))
            queue.append((i + 1, i))

        # Run AC-3
        consistent = True
        while queue:
            Xi, Xj = queue.popleft()
            if self.remove_inconsistent_values(Xi, Xj, domains):
                if not domains[Xi]:
                    consistent = False
                    break
                # Add neighbor arcs (Xi's neighbors are Xi-1 and Xi+1)
                for Xk in [Xi - 1, Xi + 1]:
                    if 0 <= Xk <= depth and Xk != Xj:
                        queue.append((Xk, Xi))

        # Total size after AC-3
        total_final_states = sum(len(domains[i]) for i in range(depth + 1)) if consistent else 0

        path = None
        if consistent:
            # 4. Find path using backtracking search on consistent domains
            path = self.backtrack_path(0, depth, domains, [self.start_state], {self.start_state})

        if path:
            self.state = "solved"
            self.solution_path = path
            self.path_cost = len(path) - 1
            
            # Add states of the path to explored
            for state in path:
                self.explored.add(state)
                self.explored_sample.append(state)

            return {
                "status": "solved",
                "node_explored": {
                    "grid": self.goal_state,
                    "flat": [v for r in self.goal_state for v in r],
                    "g": depth, "h": 0, "f": depth
                },
                "frontier_size": 0,
                "explored_size": len(self.explored),
                "frontier_sample": [],
                "explored_sample": [[v for r in item for v in r] for item in self.explored_sample],
                "log": f"🎯 Success! AC-3 found solution at depth D={depth}.\nPruned total states: {total_initial_states} -> {total_final_states}.\nPath: {self.path_cost} moves."
            }
        else:
            log_entry = {
                "status": "searching",
                "node_explored": {
                    "grid": self.current_state,
                    "flat": [v for r in self.current_state for v in r],
                    "g": depth, "h": 0, "f": depth
                },
                "frontier_size": 1,
                "explored_size": len(self.explored),
                "frontier_sample": [],
                "explored_sample": [],
                "log": f"ℹ️ AC-3 at depth D={depth} finished. Domain size: {total_initial_states} -> {total_final_states} (No consistent path). Trying D={depth + 1}..."
            }
            self.D += 1
            return log_entry

    def remove_inconsistent_values(self, Xi, Xj, domains):
        removed = False
        to_remove = set()
        for x in domains[Xi]:
            # Check if there is any y in domains[Xj] that is adjacent to x
            has_consistent_neighbor = False
            x_board = PuzzleBoard(x)
            for neighbor, _ in x_board.get_neighbors():
                if neighbor in domains[Xj]:
                    has_consistent_neighbor = True
                    break
            if not has_consistent_neighbor:
                to_remove.add(x)
                removed = True

        for x in to_remove:
            domains[Xi].remove(x)
        return removed

    def backtrack_path(self, idx, depth, domains, path, path_set):
        if idx == depth:
            if path[-1] == self.goal_state:
                return path
            return None

        curr = path[-1]
        curr_board = PuzzleBoard(curr)
        for neighbor, action in curr_board.get_neighbors():
            if neighbor in domains[idx + 1] and neighbor not in path_set:
                self.parent_map[neighbor] = (curr, action)
                path.append(neighbor)
                path_set.add(neighbor)
                
                result = self.backtrack_path(idx + 1, depth, domains, path, path_set)
                if result:
                    return result
                
                path.pop()
                path_set.remove(neighbor)
        return None

    def get_manhattan_distance(self, state):
        dist = 0
        for r in range(3):
            for c in range(3):
                val = state[r][c]
                if val != 0:
                    for gr in range(3):
                        for gc in range(3):
                            if self.goal_state[gr][gc] == val:
                                dist += abs(r - gr) + abs(c - gc)
                                break
        return dist

    def bfs_reachable(self, start, max_depth):
        reachable = {d: set() for d in range(max_depth + 1)}
        queue = [(start, 0)]
        visited = {start}
        reachable[0].add(start)
        
        while queue:
            curr, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            board = PuzzleBoard(curr)
            for neighbor, _ in board.get_neighbors():
                if neighbor not in visited:
                    visited.add(neighbor)
                    reachable[depth + 1].add(neighbor)
                    queue.append((neighbor, depth + 1))
        return reachable
