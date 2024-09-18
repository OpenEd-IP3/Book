import math
import time
import numpy as np
from ipycanvas import Canvas, hold_canvas
from shapely.geometry import Point, Polygon
from ipywidgets import Image
from IPython.display import display

class GUI:
    def __init__(self, state):

        self.state = state  # Store the car state

        # Define the canvas size with padding (20 pixels on each side)
        self.padding = 20
        self.field_size = 480
        self.canvas_size = 2 * self.padding + self.field_size

        self.mic_positions = np.array([[0, 0], [0, self.field_size], [self.field_size, self.field_size], [self.field_size, 0], [0, self.field_size / 2]])

        # Create the main canvas where everything will be drawn
        self.canvas = Canvas(width=self.canvas_size, height=self.canvas_size)

        # Draw the field area
        self.canvas.fill_style = '#DDDDDD'  # Background color for the field
        self.canvas.fill_rect(self.padding, self.padding, self.field_size, self.field_size)  # Draw the 480x480 field

        # Car dimensions
        self.car_width = 60
        self.car_height = 30

        # Create a pre-rendered canvas for the car (to optimize drawing speed)
        self.car_canvas = Canvas(width=self.car_width, height=self.car_height)
        try:
            self.car_canvas.draw_image(Image.from_file('GUI/car.png'), 0, 0, self.car_width, self.car_height)
        except FileNotFoundError:
            self.car_canvas.draw_image(Image.from_file('KITT_Simulator/GUI/car.png'), 0, 0, self.car_width, self.car_height)

        self.simulation_running = True

    def update(self):
        if not self.simulation_running:
            return
        
        self.check_collision()

        with hold_canvas(self.canvas):
            self.canvas.clear()  # Clear the main canvas to redraw the car
            # Redraw the field
            self.canvas.fill_style = '#DDDDDD'
            self.canvas.fill_rect(self.padding, self.padding, self.field_size, self.field_size)

            # Draw the microphones
            self.canvas.fill_style = 'black'
            for mic_x, mic_y in self.mic_positions:
                mic_x = mic_x + self.padding
                mic_y = self.field_size - mic_y + self.padding
                self.canvas.fill_circle(mic_x, mic_y, 3)

            # Calculate the car position with the bottom-left origin and center the car
            car_x = self.state.x + self.padding
            car_y = self.field_size - self.state.y + self.padding  # Flip y-axis for bottom-left origin

            # Apply rotation and draw the pre-rendered car canvas
            self.canvas.save()  # Save the current canvas state
            self.canvas.translate(car_x, car_y)  # Translate to the car's position
            self.canvas.rotate(-self.state.theta + np.pi)  # Rotate around the car's center

            # Draw the pre-rendered car canvas (optimized for speed)
            self.canvas.draw_image(self.car_canvas, -self.car_width / 2, -self.car_height / 2)

            if self.state.beacon:
                # Draw a blue circle on the car
                self.canvas.fill_style = 'blue'
                self.canvas.fill_circle(0, 0, 5)

            self.canvas.restore()  # Restore the canvas state to prevent affecting other drawings

    def check_collision(self):
        # Define the car polygon based on the current state
        car_polygon = Polygon([
            (self.state.x - self.car_width / 2, self.state.y - self.car_height / 2),
            (self.state.x + self.car_width / 2, self.state.y - self.car_height / 2),
            (self.state.x + self.car_width / 2, self.state.y + self.car_height / 2),
            (self.state.x - self.car_width / 2, self.state.y + self.car_height / 2)
        ])

        # Define the field boundaries as a polygon
        field_polygon = Polygon([
            (self.padding, self.padding),
            (self.padding + self.field_size, self.padding),
            (self.padding + self.field_size, self.padding + self.field_size),
            (self.padding, self.padding + self.field_size)
        ])

        # Check if the car is outside the field boundaries
        if not field_polygon.contains(Point(self.state.x, self.state.y)):
            print("Car is outside the field boundaries!")
            self.simulation_running = False

    def display(self):
        display(self.canvas)  # Ensure the canvas is displayed in the notebook

    def stop(self):
        self.simulation_running = False
        self.__del__()

    def __del__(self):
        pass