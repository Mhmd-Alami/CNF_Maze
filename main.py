from gui import MazeGUI
from logic import LocalizationKB

maze = []
with open('maze.txt') as f:
    for line in f:
        row = [int(c) for c in line.strip().split()]
        maze.append(row)

kb = LocalizationKB(maze)
gui = MazeGUI(maze, kb)
gui.run()