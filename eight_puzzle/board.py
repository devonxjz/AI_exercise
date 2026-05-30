import random

class PuzzleBoard:
    """
    Model: Tracks the state of the 3x3 8-puzzle board and validates moves/solvability.
    """
    GOAL_STATE = ((1, 2, 3), 
                  (4, 5, 6), 
                  (7, 8, 0))

    def __init__(self, state=None):
        if state is not None:
            self.state = tuple(tuple(row) for row in state)
        else:
            self.state = self.generate_random_solvable()

    @staticmethod
    def count_inversions(grid):
        """
        Calculates the number of inversions in the grid (ignoring the blank tile 0).
        """
        flat = [val for row in grid for val in row if val != 0]
        inversions = 0
        for i in range(len(flat)):
            for j in range(i + 1, len(flat)):
                if flat[i] > flat[j]:
                    inversions += 1
        return inversions

    @staticmethod
    def is_solvable(grid):
        """
        A 3x3 grid is solvable if and only if the number of inversions is even.
        """
        return PuzzleBoard.count_inversions(grid) % 2 == 0

    @staticmethod
    def generate_random_solvable():
        """
        Shuffles the tiles randomly until a mathematically solvable configuration is found.
        """
        while True:
            nums = list(range(9))
            random.shuffle(nums)
            grid = tuple(tuple(nums[i*3 : (i+1)*3]) for i in range(3))
            if PuzzleBoard.is_solvable(grid):
                return grid

    def get_neighbors(self):
        """
        Finds the empty tile 0 and moves it in valid directions (UP, DOWN, LEFT, RIGHT).
        Returns a list of tuples: (new_grid, action_taken)
        """
        grid = self.state
        r, c = -1, -1
        # Find 0 position
        for i in range(3):
            for j in range(3):
                if grid[i][j] == 0:
                    r, c = i, j
                    break
        
        neighbors = []
        moves = [(-1, 0, "UP"), (1, 0, "DOWN"), (0, -1, "LEFT"), (0, 1, "RIGHT")]
        
        for dr, dc, action in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                # Convert grid to mutable list of lists
                temp = [list(row) for row in grid]
                # Swap values
                temp[r][c], temp[nr][nc] = temp[nr][nc], temp[r][c]
                new_grid = tuple(tuple(row) for row in temp)
                neighbors.append((new_grid, action))
                
        return neighbors
