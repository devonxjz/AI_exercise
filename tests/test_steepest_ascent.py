import unittest

try:
    from eight_puzzle.algorithms.hill_climbing import SteepestAscentHillClimbingSolver
except ImportError:
    SteepestAscentHillClimbingSolver = None

class TestSteepestAscentHillClimbingSolver(unittest.TestCase):
    def setUp(self):
        self.start_state = ((1, 2, 3), (4, 5, 6), (7, 0, 8))  # 1 move away from goal
        self.goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

    def test_steepest_ascent_happy_path(self):
        if SteepestAscentHillClimbingSolver is None:
            self.fail("SteepestAscentHillClimbingSolver class does not exist yet (TDD failing test)")
        solver = SteepestAscentHillClimbingSolver(self.start_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(path[-1], self.goal_state)
        self.assertEqual(len(path), 2)  # Start state -> Goal state

    def test_steepest_ascent_edge_case(self):
        if SteepestAscentHillClimbingSolver is None:
            self.fail("SteepestAscentHillClimbingSolver class does not exist yet (TDD failing test)")
        solver = SteepestAscentHillClimbingSolver(self.goal_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], self.goal_state)

    def test_steepest_ascent_local_optimum(self):
        if SteepestAscentHillClimbingSolver is None:
            self.fail("SteepestAscentHillClimbingSolver class does not exist yet (TDD failing test)")
        # This state has h=2, and all its neighbors have h=3. It is a local optimum.
        local_optimum_state = ((1, 2, 3), (4, 5, 6), (8, 7, 0))
        solver = SteepestAscentHillClimbingSolver(local_optimum_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "unsolvable")
        self.assertEqual(len(path), 0)

if __name__ == "__main__":
    unittest.main()
