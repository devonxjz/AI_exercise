import unittest
from eight_puzzle.algorithms.backtracking_mrv import BacktrackingMRVSolver

class TestBacktrackingMRVSolver(unittest.TestCase):
    def setUp(self):
        self.start_state = ((1, 2, 3), (4, 5, 6), (7, 0, 8))  # 1 move away from goal
        self.goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

    def test_backtracking_mrv_happy_path(self):
        solver = BacktrackingMRVSolver(self.start_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(path[-1], self.goal_state)
        self.assertEqual(len(path), 2)

    def test_backtracking_mrv_edge_case(self):
        solver = BacktrackingMRVSolver(self.goal_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], self.goal_state)

    def test_backtracking_mrv_get_mrv_score(self):
        solver = BacktrackingMRVSolver(self.start_state, self.goal_state)
        # Center cell has 4 neighbors, edge has 3, corner has 2
        corner_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))
        self.assertEqual(solver.get_mrv_score(corner_state), 2)
        
        center_state = ((1, 2, 3), (4, 0, 5), (6, 7, 8))
        self.assertEqual(solver.get_mrv_score(center_state), 4)

if __name__ == "__main__":
    unittest.main()
