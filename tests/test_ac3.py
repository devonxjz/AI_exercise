import unittest
from eight_puzzle.algorithms.ac3 import AC3Solver

class TestAC3Solver(unittest.TestCase):
    def setUp(self):
        self.start_state = ((1, 2, 3), (4, 5, 6), (7, 0, 8))  # 1 move away from goal
        self.goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

    def test_ac3_happy_path(self):
        solver = AC3Solver(self.start_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(path[-1], self.goal_state)
        self.assertEqual(len(path), 2)

    def test_ac3_edge_case(self):
        solver = AC3Solver(self.goal_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], self.goal_state)

    def test_ac3_bfs_reachable(self):
        solver = AC3Solver(self.start_state, self.goal_state)
        reachable = solver.bfs_reachable(self.start_state, 1)
        self.assertIn(self.start_state, reachable[0])
        # After 1 step from start state ((1,2,3), (4,5,6), (7,0,8)), we should reach goal_state ((1,2,3), (4,5,6), (7,8,0))
        # or state ((1,2,3), (4,5,6), (0,7,8))
        self.assertIn(self.goal_state, reachable[1])
        self.assertEqual(len(reachable[1]), 3)

if __name__ == "__main__":
    unittest.main()
