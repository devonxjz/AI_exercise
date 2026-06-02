import unittest

try:
    from eight_puzzle.algorithms.simple_hill_climbing import SimpleHillClimbingSolver
except ImportError:
    SimpleHillClimbingSolver = None

class TestSimpleHillClimbingSolver(unittest.TestCase):
    def setUp(self):
        self.start_state = ((1, 2, 3), (4, 5, 6), (7, 0, 8))  # 1 move away from goal
        self.goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

    def test_simple_hill_climbing_happy_path(self):
        if SimpleHillClimbingSolver is None:
            self.fail("SimpleHillClimbingSolver class does not exist yet (TDD failing test)")
        solver = SimpleHillClimbingSolver(self.start_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(path[-1], self.goal_state)
        self.assertEqual(len(path), 2)

    def test_simple_hill_climbing_edge_case(self):
        if SimpleHillClimbingSolver is None:
            self.fail("SimpleHillClimbingSolver class does not exist yet (TDD failing test)")
        solver = SimpleHillClimbingSolver(self.goal_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], self.goal_state)

    def test_simple_hill_climbing_local_optimum(self):
        if SimpleHillClimbingSolver is None:
            self.fail("SimpleHillClimbingSolver class does not exist yet (TDD failing test)")
        # Local optimum state
        local_optimum_state = ((1, 2, 3), (4, 5, 6), (8, 7, 0))
        solver = SimpleHillClimbingSolver(local_optimum_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "unsolvable")
        self.assertEqual(len(path), 0)

if __name__ == "__main__":
    unittest.main()
