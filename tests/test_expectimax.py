import unittest
from eight_puzzle.algorithms.expectimax import ExpectimaxSolver

class TestExpectimaxSolver(unittest.TestCase):
    def setUp(self):
        self.start_state = ((1, 2, 3), (4, 5, 6), (7, 0, 8))  # 1 move away from goal
        self.goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

    def test_expectimax_happy_path(self):
        # Arrange & Act
        solver = ExpectimaxSolver(self.start_state, self.goal_state, depth=3)
        path = solver.solve_all()
        # Assert
        self.assertEqual(solver.state, "solved")
        self.assertEqual(path[-1], self.goal_state)
        self.assertEqual(len(path), 2)

    def test_expectimax_edge_case(self):
        # Arrange & Act
        solver = ExpectimaxSolver(self.goal_state, self.goal_state, depth=3)
        path = solver.solve_all()
        # Assert
        self.assertEqual(solver.state, "solved")
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], self.goal_state)

if __name__ == "__main__":
    unittest.main()
