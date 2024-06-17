import tkinter as tk
import numpy as np
import math

class Micarray:
    def __init__(self, canvas):
        self.canvas = canvas
        self.position = np.array([0,0])
        self.Fs = None
        self.num_samples = None
        self.draw_micarray()
        self.orientation = np.array([0, -1])

    def draw_micarray(self):
        self.canvas.delete("micarray")
        micarray_length = 10
        micarray_width = 10

        center_x, center_y = self.position
        dx, dy = self.orientation
        perp_dx, perp_dy = -dy, dx

        # Coordinates of each corner
        corners = [
            (center_x + 0.5 * micarray_length * dx + 0.5 * micarray_width * -dy,
                center_y + 0.5 * micarray_length * dy + 0.5 * micarray_width * dx),
            (center_x + 0.5 * micarray_length * dx - 0.5 * micarray_width * -dy,
                center_y + 0.5 * micarray_length * dy - 0.5 * micarray_width * dx),
            (center_x - 0.5 * micarray_length * dx - 0.5 * micarray_width * -dy,
                center_y - 0.5 * micarray_length * dy - 0.5 * micarray_width * dx),
            (center_x - 0.5 * micarray_length * dx + 0.5 * micarray_width * -dy,
                center_y - 0.5 * micarray_length * dy + 0.5 * micarray_width * dx)
        ]

        self.canvas.create_polygon(corners, fill='', outline='black', tags="micarray")

class Beacon:
    def __init__(self, canvas):
        self.canvas = canvas
        self.position = np.array([0,0])
        self.orientation = np.array([0, -1])
        self.angle =0
        self.draw_beacon()

    def draw_beacon(self):
        self.canvas.delete("beacon")
        beacon_length = 10
        beacon_width = 10

        center_x, center_y = self.position
        dx, dy = self.orientation
        perp_dx, perp_dy = -dy, dx

        # Coordinates of each corner
        corners = [
            (center_x + 0.5 * beacon_length * dx + 0.5 * beacon_width * -dy,
                center_y + 0.5 * beacon_length * dy + 0.5 * beacon_width * dx),
            (center_x + 0.5 * beacon_length * dx - 0.5 * beacon_width * -dy,
                center_y + 0.5 * beacon_length * dy - 0.5 * beacon_width * dx),
            (center_x - 0.5 * beacon_length * dx - 0.5 * beacon_width * -dy,
                center_y - 0.5 * beacon_length * dy - 0.5 * beacon_width * dx),
            (center_x - 0.5 * beacon_length * dx + 0.5 * beacon_width * -dy,
                center_y - 0.5 * beacon_length * dy + 0.5 * beacon_width * dx)
        ]

        self.canvas.create_polygon(corners, fill='', outline='black', tags="beacon")