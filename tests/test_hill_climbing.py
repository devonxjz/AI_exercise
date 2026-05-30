import unittest

try:
    from eight_puzzle.algorithms.hill_climbing import HillClimbingSolver
except ImportError:
    HillClimbingSolver = None

class TestHillClimbingSolver(unittest.TestCase):
    def setUp(self):
        self.start_state = ((1, 2, 3), (4, 5, 6), (7, 0, 8))  # 1 move away from goal
        self.goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

    def test_hill_climbing_solver_happy_path(self):
        if HillClimbingSolver is None:
            self.fail("HillClimbingSolver class does not exist yet (TDD failing test)")
        solver = HillClimbingSolver(self.start_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(path[-1], self.goal_state)
        self.assertEqual(len(path), 2)  # Start state -> Goal state

    def test_hill_climbing_solver_edge_case(self):
        if HillClimbingSolver is None:
            self.fail("HillClimbingSolver class does not exist yet (TDD failing test)")
        solver = HillClimbingSolver(self.goal_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], self.goal_state)

    def test_hill_climbing_solver_local_optimum(self):
        if HillClimbingSolver is None:
            self.fail("HillClimbingSolver class does not exist yet (TDD failing test)")
        # This state has h=2, and all its neighbors have h=3. It is a local optimum.
        local_optimum_state = ((1, 2, 3), (4, 5, 6), (8, 7, 0))
        solver = HillClimbingSolver(local_optimum_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "unsolvable")
        # Path should contain only the start state since we got stuck immediately
        self.assertEqual(len(path), 0)

if __name__ == "__main__":
    unittest.main()
