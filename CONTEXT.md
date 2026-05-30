# Glossary: 8-Puzzle Domain Map

## Terms

### PuzzleState
A 3x3 grid representation of the 8-puzzle board. Represented as a hashable, immutable `tuple` of `tuples` of integers from 0 to 8, where 0 denotes the empty cell.

### Goal State
The target layout of the puzzle where tiles are ordered sequentially:
```
1 2 3
4 5 6
7 8 0
```
Represented as `((1, 2, 3), (4, 5, 6), (7, 8, 0))`.

### Inversion
Any pair of tiles $(a, b)$ such that $a > b$ and $a$ appears before $b$ in the row-major flat sequence of the board (excluding the empty cell 0).

### Solvable State
A board layout that can reach the Goal State through valid sliding moves. In a 3x3 board, a state is solvable if and only if its number of inversions is even.

### Solver
A search algorithm adapter that implements the `BaseSolver` interface. It resolves a starting `PuzzleState` to the `Goal State`.

### Frontier
The set of discovered board states that have not yet been expanded. Also known as the Open List.

### Explored Set
The set of expanded board states that have already been visited. Also known as the Closed List.
