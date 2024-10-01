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

        # Create a pre-rendered canvas for the explosion
        self.explosion_canvas = Canvas(width=200, height=200)
        try:
            self.explosion_canvas.draw_image(Image.from_file('GUI/explosion.png'), 0, 0, 200, 200)
        except FileNotFoundError:
            self.explosion_canvas.draw_image(Image.from_file('KITT_Simulator/GUI/explosion.png'), 0, 0, 200, 200)

        self.simulation_running = True

        self.prev_positions = []

    def update(self):
        if not self.simulation_running:
            return

        collision_detected = self.check_collision()
        self.calculate_distance_to_wall()

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

            self.canvas.fill_style = 'black'
            self.canvas.fill_text(f"M{self.state.motor_command}", self.field_size - 20, 20 + self.padding)
            self.canvas.fill_text(f"D{self.state.servo_command}", self.field_size - 20, 30 + self.padding)
            self.canvas.fill_text(f"L{self.state.dist_L:.2f}", self.field_size - 20, 40 + self.padding)
            self.canvas.fill_text(f"R{self.state.dist_R:.2f}", self.field_size - 20, 50 + self.padding)

            # Calculate the car position with the bottom-left origin and center the car
            car_x = self.state.x + self.padding
            car_y = self.field_size - self.state.y + self.padding  # Flip y-axis for bottom-left origin

            # Track the previous positions
            self.prev_positions.append((car_x, car_y))
            # Draw the car's previous 1000 positions
            for i in range(len(self.prev_positions)):
                if i == len(self.prev_positions) - 1:
                    break
                self.canvas.fill_style = 'grey'
                self.canvas.fill_circle(self.prev_positions[i][0], self.prev_positions[i][1], 1)

            if collision_detected:
                # Draw the explosion image at the car's location
                self.canvas.draw_image(self.explosion_canvas, car_x - 100, car_y - 100, 200, 200)
                self.simulation_running = False  # Stop simulation after collision
            else:
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
            return True
        
        return False
    
    def calculate_distance_to_wall(self):
        """
        Calculates the distance from the front-left and front-right corners of the car to the nearest wall
        the car is facing, considering the car's orientation within a square field.
        """

        # Car's dimensions
        w = self.car_width
        h = self.car_height

        # Car's position and orientation
        x_car = self.state.x
        y_car = self.state.y
        theta = self.state.theta

        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)

        # Front-left corner in local coordinates (corrected to front)
        x_fl_local = w / 2
        y_fl_local = h / 2

        # Front-right corner in local coordinates (corrected to front)
        x_fr_local = w / 2
        y_fr_local = -h / 2

        # Compute global positions of the front-left corner
        x_fl_global = x_car + x_fl_local * cos_theta - y_fl_local * sin_theta
        y_fl_global = y_car + x_fl_local * sin_theta + y_fl_local * cos_theta

        # Compute global positions of the front-right corner
        x_fr_global = x_car + x_fr_local * cos_theta - y_fr_local * sin_theta
        y_fr_global = y_car + x_fr_local * sin_theta + y_fr_local * cos_theta

        # Direction vector (normalized)
        dir_x = cos_theta
        dir_y = sin_theta

        # Function to compute distance to walls from a point
        def distance_to_walls(x0, y0, dir_x, dir_y):
            t_values = []

            # Left wall x = 0
            if dir_x != 0:
                t = (0 - x0) / dir_x
                if t > 0:
                    y = y0 + t * dir_y
                    if 0 <= y <= self.field_size:
                        t_values.append(t)
            # Right wall x = self.field_size
            if dir_x != 0:
                t = (self.field_size - x0) / dir_x
                if t > 0:
                    y = y0 + t * dir_y
                    if 0 <= y <= self.field_size:
                        t_values.append(t)
            # Bottom wall y = 0
            if dir_y != 0:
                t = (0 - y0) / dir_y
                if t > 0:
                    x = x0 + t * dir_x
                    if 0 <= x <= self.field_size:
                        t_values.append(t)
            # Top wall y = self.field_size
            if dir_y != 0:
                t = (self.field_size - y0) / dir_y
                if t > 0:
                    x = x0 + t * dir_x
                    if 0 <= x <= self.field_size:
                        t_values.append(t)

            if t_values:
                return min(t_values)
            else:
                return float('inf')  # No intersection in the positive t direction

        # Compute distances from the front-left and front-right corners
        dist_L = distance_to_walls(x_fl_global, y_fl_global, dir_x, dir_y)
        dist_R = distance_to_walls(x_fr_global, y_fr_global, dir_x, dir_y)

        # Update the state with the computed distances
        self.state.dist_L = dist_L
        self.state.dist_R = dist_R

    def display(self):
        display(self.canvas)  # Ensure the canvas is displayed in the notebook

    def stop(self):
        self.simulation_running = False
        self.__del__()

    def __del__(self):
        pass

# Usage:
# state = State()
# gui = GUI(state)
# gui.display()
# for i in range(100):
#     state.x = i
#     state.y = 2 * i
#     state.theta = np.pi / 2 + i / 100
#     gui.update()
#     time.sleep(0.5)
# gui.stop()