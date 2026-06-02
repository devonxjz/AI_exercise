import unittest
import tkinter as tk
from eight_puzzle.ui import EightPuzzleApp
from eight_puzzle.board import PuzzleBoard

class TestUIFailures(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        # Use a mathematically solvable state that gets stuck in Hill Climbing
        self.local_optimum_state = ((5, 7, 8), (2, 1, 3), (6, 0, 4))
        
        # Override generate_random_solvable to return this state
        self.orig_random = PuzzleBoard.generate_random_solvable
        PuzzleBoard.generate_random_solvable = lambda: self.local_optimum_state
        
        self.app = EightPuzzleApp(self.root)

    def tearDown(self):
        PuzzleBoard.generate_random_solvable = self.orig_random
        self.root.destroy()

    def test_ui_solve_instantly_failure_logging(self):
        # Switch to Steepest-ascent Hill Climbing
        self.app.algo_combobox.set("Steepest-ascent Hill Climbing")
        self.app.on_algo_changed()
        
        # Trigger solve instantly. It runs in a background thread, but we can call the background
        # method directly for testing.
        self.app.solve_instantly_background()
        
        # Process pending Tkinter events (like root.after callbacks)
        self.root.update()
        
        # Check that the status is set to FAILED
        self.assertEqual(self.app.stat_status.cget("text"), "FAILED")
        
        # Check that the log in console_text contains details about stuck/failure state
        console_content = self.app.console_text.get("1.0", tk.END)
        self.assertIn("Stuck in local optimum", console_content)
        self.assertIn("Search failed / unsolvable state", console_content)

    def test_ui_step_search_failure_logging(self):
        # Switch to Simple Hill Climbing
        self.app.algo_combobox.set("Simple Hill Climbing")
        self.app.on_algo_changed()
        
        # Step through until we get stuck (since it's a local optimum, it will get stuck in a few steps)
        while self.app.engine.state == "searching" or self.app.engine.state == "idle":
            self.app.on_step_search()
            if self.app.engine.state in ("solved", "unsolvable"):
                break
        
        # Check that status is set to FAILED and error message is printed
        self.assertEqual(self.app.stat_status.cget("text"), "FAILED")
        console_content = self.app.console_text.get("1.0", tk.END)
        self.assertIn("Stuck in local optimum", console_content)
        self.assertIn("Search failed / unsolvable state", console_content)

if __name__ == "__main__":
    unittest.main()
