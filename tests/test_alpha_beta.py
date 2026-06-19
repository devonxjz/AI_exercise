import unittest
from eight_puzzle.algorithms.alpha_beta import AlphaBetaSolver
from eight_puzzle.algorithms.minimax import MinimaxSolver

class TestAlphaBetaSolver(unittest.TestCase):
    def setUp(self):
        self.start_state = ((1, 2, 3), (4, 5, 6), (7, 0, 8))  # 1 move away from goal
        self.goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

    def test_alpha_beta_happy_path(self):
        # Arrange & Act
        solver = AlphaBetaSolver(self.start_state, self.goal_state, depth=3)
        path = solver.solve_all()
        # Assert
        self.assertEqual(solver.state, "solved")
        self.assertEqual(path[-1], self.goal_state)
        self.assertEqual(len(path), 2)

    def test_alpha_beta_edge_case(self):
        # Arrange & Act
        solver = AlphaBetaSolver(self.goal_state, self.goal_state, depth=3)
        path = solver.solve_all()
        # Assert
        self.assertEqual(solver.state, "solved")
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], self.goal_state)

    def test_alpha_beta_pruning_effectiveness(self):
        # Arrange: Use a slightly more complex board state where pruning can occur
        # State: ((1, 2, 3), (4, 0, 5), (7, 8, 6)) -> 2 moves from goal
        complex_start = ((1, 2, 3), (4, 0, 5), (7, 8, 6))
        
        # Act
        minimax_solver = MinimaxSolver(complex_start, self.goal_state, depth=4)
        minimax_solver.init_search()
        minimax_solver.step_search()
        
        ab_solver = AlphaBetaSolver(complex_start, self.goal_state, depth=4)
        ab_solver.init_search()
        ab_solver.step_search()
        
        # Assert: Both should find the same best next state
        self.assertEqual(ab_solver.current_state, minimax_solver.current_state)
        # And Alpha-Beta should expand fewer or equal nodes than Minimax due to pruning
        self.assertLessEqual(ab_solver.nodes_expanded, minimax_solver.nodes_expanded)

if __name__ == "__main__":
    unittest.main()
