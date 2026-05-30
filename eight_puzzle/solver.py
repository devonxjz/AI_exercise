from collections import deque
from abc import ABC, abstractmethod
from eight_puzzle.board import PuzzleBoard

class BaseSolver(ABC):
    """
    Interface (Seam) for all puzzle solvers.
    Encapsulates the standard lifecycle of step-by-step search, stats tracking, and path reconstruction.
    """
    def __init__(self, start_state, goal_state=PuzzleBoard.GOAL_STATE):
        self.start_state = tuple(tuple(row) for row in start_state)
        self.goal_state = tuple(tuple(row) for row in goal_state)
        self.current_state = self.start_state
        
        # Search state variables
        self.state = "idle"       # "idle", "searching", "solved", "unsolvable"
        self.nodes_expanded = 0
        self.max_frontier_size = 0
        self.solution_path = []
        self.path_cost = 0
        
        # Standard tracking maps
        self.parent_map = {self.start_state: (None, None)}
        self.explored = set()
        self.explored_sample = deque(maxlen=5) # O(1) sliding deque for tracking the last 5 explored nodes

    def init_search(self):
        """
        Prepares the common solver data structures and stats.
        Subclasses should call super().init_search() to reset these variables.
        """
        self.state = "searching"
        self.nodes_expanded = 0
        self.max_frontier_size = 1
        self.solution_path = []
        self.path_cost = 0
        self.parent_map = {self.start_state: (None, None)}
        self.g_map = {self.start_state: 0}
        self.explored = set()
        self.explored_sample = deque(maxlen=5)

    @abstractmethod
    def step_search(self):
        """
        Performs ONE expansion step.
        Returns a log dictionary of search state for the UI, or None if search is inactive.
        """
        pass

    def solve_all(self):
        """
        Executes search completely to find a solution.
        """
        self.init_search()
        while self.state == "searching":
            self.step_search()
        return self.solution_path

    def reconstruct_path(self):
        """
        Traces parent pointers back from goal state to start state.
        """
        path = []
        curr = self.goal_state
        while curr is not None:
            path.append(curr)
            curr, _ = self.parent_map.get(curr, (None, None))
        path.reverse()
        self.solution_path = path
        self.path_cost = len(path) - 1
