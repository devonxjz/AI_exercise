import unittest
from eight_puzzle.algorithms.minimax import MinimaxSolver

class TestMinimaxSolver(unittest.TestCase):
    def setUp(self):
        self.start_state = ((1, 2, 3), (4, 5, 6), (7, 0, 8))  # 1 move away from goal
        self.goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

    def test_minimax_happy_path(self):
        # Arrange & Act
        solver = MinimaxSolver(self.start_state, self.goal_state, depth=3)
        path = solver.solve_all()
        # Assert
        self.assertEqual(solver.state, "solved")
        self.assertEqual(path[-1], self.goal_state)
        self.assertEqual(len(path), 2)

    def test_minimax_edge_case(self):
        # Arrange & Act
        solver = MinimaxSolver(self.goal_state, self.goal_state, depth=3)
        path = solver.solve_all()
        # Assert
        self.assertEqual(solver.state, "solved")
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], self.goal_state)

    def test_minimax_depth_customization(self):
        # Arrange
        solver = MinimaxSolver(self.start_state, self.goal_state, depth=1)
        # Act
        solver.init_search()
        log = solver.step_search()
        # Assert
        self.assertEqual(solver.search_depth, 1)
        self.assertIsNotNone(log)

if __name__ == "__main__":
    unittest.main()
