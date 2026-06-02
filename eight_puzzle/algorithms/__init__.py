from eight_puzzle.algorithms.bfs import BFSSolver
from eight_puzzle.algorithms.dfs import DFSSolver
from eight_puzzle.algorithms.ucs import UCSSolver
from eight_puzzle.algorithms.a_star import AStarSolver
from eight_puzzle.algorithms.greedy import GreedySolver
from eight_puzzle.algorithms.hill_climbing import HillClimbingSolver, SteepestAscentHillClimbingSolver
from eight_puzzle.algorithms.simple_hill_climbing import SimpleHillClimbingSolver
from eight_puzzle.algorithms.stochastic_hill_climbing import StochasticHillClimbingSolver
from eight_puzzle.algorithms.local_beam_search import LocalBeamSearchSolver

# Manual Registry of Solvers
SOLVER_REGISTRY = {
    "BFS (Breadth-First Search)": BFSSolver,
    "DFS (Depth-First Search)": DFSSolver,
    "UCS (Uniform Cost Search)": UCSSolver,
    "A* Search (Manhattan Distance)": AStarSolver,
    "Greedy Best-First Search": GreedySolver,
    "Hill Climbing (Local Search)": HillClimbingSolver,
    "Simple Hill Climbing": SimpleHillClimbingSolver,
    "Steepest-ascent Hill Climbing": SteepestAscentHillClimbingSolver,
    "Stochastic Hill Climbing": StochasticHillClimbingSolver,
    "Local Beam Search": LocalBeamSearchSolver
}

# Theme definitions for each algorithm
ALGORITHM_THEMES = {
    "BFS (Breadth-First Search)": {
        "accent": "#A6E3A1",      # Pastel Green
        "accent_bg": "#253825",
        "description": "Heuristic: None (Breadth-First Search)"
    },
    "DFS (Depth-First Search)": {
        "accent": "#F5C2E7",      # Pastel Pink
        "accent_bg": "#382535",
        "description": "Heuristic: None (Depth-First Search - Stack LIFO, max depth 50)"
    },
    "UCS (Uniform Cost Search)": {
        "accent": "#89B4FA",      # Pastel Blue
        "accent_bg": "#252B38",
        "description": "Heuristic: None (Path cost g(n) priority)"
    },
    "A* Search (Manhattan Distance)": {
        "accent": "#F9E2AF",      # Pastel Yellow
        "accent_bg": "#383125",
        "description": "Heuristic: Manhattan Distance (Sum of block offsets)"
    },
    "Greedy Best-First Search": {
        "accent": "#FAB387",      # Pastel Peach/Orange
        "accent_bg": "#382A25",
        "description": "Heuristic: Manhattan Distance (Greedy Best-First Search)"
    },
    "Hill Climbing (Local Search)": {
        "accent": "#CBA6F7",      # Pastel Lavender
        "accent_bg": "#3E2E4F",
        "description": "Heuristic: Manhattan Distance (Simple Hill Climbing - stops if no neighbor is strictly better)"
    },
    "Simple Hill Climbing": {
        "accent": "#A6E3A1",      # Pastel Green
        "accent_bg": "#253825",
        "description": "Heuristic: Manhattan Distance (Simple Hill Climbing - first improving neighbor)"
    },
    "Steepest-ascent Hill Climbing": {
        "accent": "#CBA6F7",      # Pastel Lavender
        "accent_bg": "#3E2E4F",
        "description": "Heuristic: Manhattan Distance (Steepest-ascent Hill Climbing - best improving neighbor)"
    },
    "Stochastic Hill Climbing": {
        "accent": "#F38BA8",      # Pastel Red
        "accent_bg": "#3F2C32",
        "description": "Heuristic: Manhattan Distance (Stochastic Hill Climbing - random improving neighbor)"
    },
    "Local Beam Search": {
        "accent": "#89DCEB",      # Sky Blue
        "accent_bg": "#25373B",
        "description": "Heuristic: Manhattan Distance (Local Beam Search - width k=3)"
    }
}


