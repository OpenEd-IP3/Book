import math
import time
import numpy as np
from ipycanvas import Canvas
from shapely.geometry import Point, Polygon
import ipywidgets as widgets
from IPython.display import display

class Mic:
    def __init__(self, id, position):
        self.id = id
        self.position = position

    def plot(self, canvas):
        x, y, _ = self.position
        canvas.fill_style = 'blue'
        canvas.fill_circle(x, y, 5)
        canvas.stroke_style = 'black'
        canvas.stroke_circle(x, y, 5)
        canvas.fill_style = 'black'
        canvas.fill_text(str(self.id), x + 7, y + 2)

class Arena:
    def __init__(self, canvas):
        self.canvas = canvas
        self.obstacles = [
            [(200, 200), (260, 200), (260, 240), (230, 240)],
            [(350, 200), (410, 200), (410, 240), (380, 240)]
        ]
        self.waypoints = [
            (360, 360, 20)
        ]
        self.boundaries = [13, 13, 517, 517]
        self.inner_boundaries = [13, 13, 517, 517]
        self.outer_boundaries = [8, 8, 522, 522]
        self.mic_positions = [
            (12, 12, 0),
            (517, 12, 0),
            (12, 517, 0),
            (517, 517, 0)
        ]
        self.mics = [Mic(i + 1, pos) for i, pos in enumerate(self.mic_positions)]
        self.drawn = False  # To check if the arena is already drawn

    def draw(self):
        if not self.drawn:
            # Draw outer boundaries
            self.canvas.fill_style = '#808080'
            self.canvas.fill_rect(self.outer_boundaries[0], self.outer_boundaries[1],
                                  self.outer_boundaries[2] - self.outer_boundaries[0],
                                  self.outer_boundaries[3] - self.outer_boundaries[1])
            
            # Draw inner boundaries
            self.canvas.fill_style = 'white'
            self.canvas.fill_rect(self.inner_boundaries[0], self.inner_boundaries[1],
                                  self.inner_boundaries[2] - self.inner_boundaries[0],
                                  self.inner_boundaries[3] - self.inner_boundaries[1])
            
            # Draw boundaries
            self.canvas.stroke_style = 'red'
            self.canvas.set_line_dash([4, 2])
            self.canvas.stroke_rect(self.boundaries[0], self.boundaries[1],
                                    self.boundaries[2] - self.boundaries[0],
                                    self.boundaries[3] - self.boundaries[1])
            self.canvas.set_line_dash([])  # reset line dash
            
            self.canvas.fill_style = 'salmon'
            self.canvas.stroke_style = 'black'
            for obstacle in self.obstacles:
                self.canvas.fill_polygon(obstacle)
                self.canvas.stroke_polygon(obstacle)
            
            self.canvas.fill_style = 'red'
            for waypoint in self.waypoints:
                x, y, radius = waypoint
                self.canvas.fill_circle(x, y, radius)
                self.canvas.stroke_circle(x, y, radius)
            
            for mic in self.mics:
                mic.plot(self.canvas)

            self.drawn = True  # Mark arena as drawn

    def point_in_polygon(self, x, y, polygon):
        point = Point(x, y)
        poly = Polygon(polygon)
        return point.within(poly)