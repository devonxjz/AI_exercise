import unittest
from eight_puzzle.board import PuzzleBoard
from eight_puzzle.algorithms.bfs import BFSSolver
from eight_puzzle.algorithms.dfs import DFSSolver
from eight_puzzle.algorithms.ucs import UCSSolver
from eight_puzzle.algorithms.a_star import AStarSolver

class TestEightPuzzleBoard(unittest.TestCase):
    def test_inversions(self):
        # Goal state has 0 inversions
        grid = ((1, 2, 3), (4, 5, 6), (7, 8, 0))
        self.assertEqual(PuzzleBoard.count_inversions(grid), 0)
        self.assertTrue(PuzzleBoard.is_solvable(grid))
        
        # Solvable configuration: 2 inversions (even)
        grid_solvable = ((1, 2, 3), (4, 0, 6), (7, 5, 8))
        self.assertEqual(PuzzleBoard.count_inversions(grid_solvable), 2)
        self.assertTrue(PuzzleBoard.is_solvable(grid_solvable))
        
        # Unsolvable configuration: 1 inversion (odd)
        grid_unsolvable = ((1, 2, 3), (4, 5, 6), (8, 7, 0))
        self.assertEqual(PuzzleBoard.count_inversions(grid_unsolvable), 1)
        self.assertFalse(PuzzleBoard.is_solvable(grid_unsolvable))

    def test_neighbors(self):
        # Center empty cell: 4 neighbors
        grid = ((1, 2, 3), (4, 0, 5), (6, 7, 8))
        board = PuzzleBoard(grid)
        neighbors = board.get_neighbors()
        self.assertEqual(len(neighbors), 4)
        
        # Corner empty cell: 2 neighbors
        grid_corner = ((1, 2, 3), (4, 5, 6), (7, 8, 0))
        board_corner = PuzzleBoard(grid_corner)
        neighbors_corner = board_corner.get_neighbors()
        self.assertEqual(len(neighbors_corner), 2)


class TestEightPuzzleSolvers(unittest.TestCase):
    def setUp(self):
        # Easy solvable starting state (1 step from goal, empty cell at bottom-center)
        self.start_state = ((1, 2, 3), (4, 5, 6), (7, 0, 8))
        self.goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

    def test_bfs_solver(self):
        solver = BFSSolver(self.start_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(len(path) - 1, 1) # 1 step path
        self.assertEqual(path[-1], self.goal_state)

    def test_dfs_solver(self):
        solver = DFSSolver(self.start_state, self.goal_state)
        path = solver.solve_all()
        self.assertTrue(len(path) >= 1)
        self.assertEqual(path[-1], self.goal_state)

    def test_ucs_solver(self):
        solver = UCSSolver(self.start_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(len(path) - 1, 1)
        self.assertEqual(path[-1], self.goal_state)

    def test_a_star_solver(self):
        solver = AStarSolver(self.start_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(len(path) - 1, 1)
        self.assertEqual(path[-1], self.goal_state)

    def test_greedy_solver(self):
        from eight_puzzle.algorithms.greedy import GreedySolver
        solver = GreedySolver(self.start_state, self.goal_state)
        path = solver.solve_all()
        self.assertEqual(len(path) - 1, 1)
        self.assertEqual(path[-1], self.goal_state)

if __name__ == "__main__":
    unittest.main()
