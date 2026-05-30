import unittest

# Import will fail initially because the greedy module is not yet implemented
try:
    from eight_puzzle.algorithms.greedy import GreedySolver
except ImportError:
    GreedySolver = None

class TestGreedySolver(unittest.TestCase):
    def setUp(self):
        self.start_state = ((1, 2, 3), (4, 5, 6), (7, 0, 8))
        self.goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))
        
    def test_greedy_solver_happy_path(self):
        if GreedySolver is None:
            self.fail("GreedySolver class does not exist yet (TDD failing test)")
        solver = GreedySolver(self.start_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(path[-1], self.goal_state)

    def test_greedy_solver_edge_case(self):
        if GreedySolver is None:
            self.fail("GreedySolver class does not exist yet (TDD failing test)")
        # Start state is already the goal state
        solver = GreedySolver(self.goal_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(len(path), 1)

    def test_greedy_solver_unsolvable(self):
        if GreedySolver is None:
            self.fail("GreedySolver class does not exist yet (TDD failing test)")
        unsolvable_state = ((1, 2, 3), (4, 5, 6), (8, 7, 0))
        solver = GreedySolver(unsolvable_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "unsolvable")

if __name__ == "__main__":
    unittest.main()
