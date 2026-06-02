import unittest

try:
    from eight_puzzle.algorithms.local_beam_search import LocalBeamSearchSolver
except ImportError:
    LocalBeamSearchSolver = None

class TestLocalBeamSearchSolver(unittest.TestCase):
    def setUp(self):
        self.start_state = ((1, 2, 3), (4, 5, 6), (7, 0, 8))  # 1 move away from goal
        self.goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

    def test_local_beam_search_happy_path(self):
        if LocalBeamSearchSolver is None:
            self.fail("LocalBeamSearchSolver class does not exist yet (TDD failing test)")
        solver = LocalBeamSearchSolver(self.start_state, self.goal_state, k=3)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(path[-1], self.goal_state)
        self.assertEqual(len(path), 2)

    def test_local_beam_search_edge_case(self):
        if LocalBeamSearchSolver is None:
            self.fail("LocalBeamSearchSolver class does not exist yet (TDD failing test)")
        solver = LocalBeamSearchSolver(self.goal_state, self.goal_state, k=3)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], self.goal_state)

    def test_local_beam_search_unsolvable(self):
        if LocalBeamSearchSolver is None:
            self.fail("LocalBeamSearchSolver class does not exist yet (TDD failing test)")
        # An unsolvable 8-puzzle board configuration (odd inversions)
        unsolvable_state = ((1, 2, 3), (4, 5, 6), (8, 7, 0))
        solver = LocalBeamSearchSolver(unsolvable_state, self.goal_state, k=3)
        path = solver.solve_all()
        self.assertEqual(solver.state, "unsolvable")
        self.assertEqual(len(path), 0)

if __name__ == "__main__":
    unittest.main()
