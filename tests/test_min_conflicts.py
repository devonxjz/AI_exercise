import unittest
from eight_puzzle.algorithms.min_conflicts import MinConflictsSolver

class TestMinConflictsSolver(unittest.TestCase):
    def setUp(self):
        self.start_state = ((1, 2, 3), (4, 5, 6), (7, 0, 8))  # 1 move away from goal
        self.goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

    def test_min_conflicts_happy_path(self):
        solver = MinConflictsSolver(self.start_state, self.goal_state, seed=42)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(path[-1], self.goal_state)
        self.assertEqual(len(path), 2)

    def test_min_conflicts_edge_case(self):
        solver = MinConflictsSolver(self.goal_state, self.goal_state, seed=42)
        path = solver.solve_all()
        self.assertEqual(solver.state, "solved")
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], self.goal_state)

    def test_min_conflicts_count_conflicts(self):
        solver = MinConflictsSolver(self.start_state, self.goal_state, seed=42)
        # Start state has 1 misplaced tile (8 is at col 2 instead of col 1, 0 is at col 1 instead of col 2 but we ignore 0 in count_conflicts)
        # Wait, let's check: in start_state ((1,2,3), (4,5,6), (7,0,8))
        # and goal_state ((1,2,3), (4,5,6), (7,8,0)).
        # Tile 8 is at index (2, 2) in start_state. In goal_state it is at (2, 1). So it is misplaced.
        # Other non-zero tiles are at correct positions.
        # So count_conflicts should return 1.
        self.assertEqual(solver.count_conflicts(self.start_state), 1)
        self.assertEqual(solver.count_conflicts(self.goal_state), 0)

if __name__ == "__main__":
    unittest.main()
