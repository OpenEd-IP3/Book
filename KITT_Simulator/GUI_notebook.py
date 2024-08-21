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
