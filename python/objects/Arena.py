import tkinter as tk

class Arena:
    def __init__(self, canvas):
        self.canvas = canvas
        self.obstacles = [
            (200, 200, 260, 200, 260, 240, 230, 240),
            (350, 200, 410, 200, 410, 240, 380, 240)
        ]
        self.waypoints = [
            (400, 400, 420, 420)
        ]

    def draw(self):
        self.canvas.create_rectangle(50, 50, 550, 550, dash=(4, 2), outline="red", tags="arena")
        for obstacle in self.obstacles:
            self.canvas.create_polygon(obstacle, fill="salmon", outline="black", tags="arena")
        for waypoint in self.waypoints:
            self.canvas.create_oval(waypoint, fill="red", outline="black", tags="arena")