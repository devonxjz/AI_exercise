import tkinter as tk
from eight_puzzle.ui import EightPuzzleApp

if __name__ == "__main__":
    # Launch modular 8-puzzle simulator
    root = tk.Tk()
    app = EightPuzzleApp(root)
    root.mainloop()
