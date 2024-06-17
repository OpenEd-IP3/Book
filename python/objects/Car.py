import tkinter as tk
import numpy as np
import math

class state:
    x: float
    y: float
    theta: float
    # v: float
    last_update: float

class Car:
    def __init__(self, canvas):
        self.canvas = canvas
        self.position = np.array([90, 550])
        self.orientation = np.array([0, -1])
        self.angle =0
        self.draw_car()

    def draw_car(self):
        self.canvas.delete("car")
        car_length = 42  # length
        car_width = 20  # width

        center_x, center_y = self.position
        dx, dy = self.orientation
        perp_dx, perp_dy = -dy, dx

        # Coordinates of each corner
        corners = [
            (center_x + 0.5 * car_length * dx + 0.5 * car_width * -dy,
             center_y + 0.5 * car_length * dy + 0.5 * car_width * dx),
            (center_x + 0.5 * car_length * dx - 0.5 * car_width * -dy,
             center_y + 0.5 * car_length * dy - 0.5 * car_width * dx),
            (center_x - 0.5 * car_length * dx - 0.5 * car_width * -dy,
             center_y - 0.5 * car_length * dy - 0.5 * car_width * dx),
            (center_x - 0.5 * car_length * dx + 0.5 * car_width * -dy,
             center_y - 0.5 * car_length * dy + 0.5 * car_width * dx)
        ]

        self.canvas.create_polygon(corners, fill='', outline='black', tags="car")
        wheel_length = 10
        wheel_width = 3
        wheel_color = 'blue'
        wheel_offset = 5

        # Front wheels
        rot_angle = self.angle
        cos_a, sin_a = math.cos(rot_angle), math.sin(rot_angle)
        front_wheels = [
            np.array(corners[0]) + wheel_offset * np.array([perp_dx, perp_dy]),  # f left
            np.array(corners[1]) + wheel_offset * np.array([-perp_dx, -perp_dy])   # f right
        ]
        for corner in front_wheels:
            wheel_start = corner
            wheel_end = wheel_start + wheel_length * np.array([cos_a * dx - sin_a * dy, sin_a * dx + cos_a * dy])
            self.canvas.create_line(wheel_start[0], wheel_start[1], wheel_end[0], wheel_end[1],
                                    width=wheel_width, fill=wheel_color,  tags="car")

        # Back wheels
        back_wheels = [
            np.array(corners[2]) + wheel_offset * np.array([-perp_dx, -perp_dy]),  # r right
            np.array(corners[3]) + wheel_offset * np.array([perp_dx, perp_dy])   # r left
        ]
        for corner in back_wheels:
            wheel_start = corner
            wheel_end = wheel_start - wheel_length * np.array([dx, dy])
            self.canvas.create_line(wheel_start[0], wheel_start[1], wheel_end[0], wheel_end[1],
                                    width=wheel_width, fill=wheel_color, tags="car")
    def update_orientation(self, angle_degrees):
        angle_radians = math.radians(angle_degrees)
        angle_radius = self.angle + angle_radians
        cos_a, sin_a = math.cos(angle_radians), math.sin(angle_radius)
        new_dx = cos_a * self.orientation[0] - sin_a * self.orientation[1]
        new_dy = sin_a * self.orientation[0] + cos_a * self.orientation[1]
        self.orientation = np.array([new_dx, new_dy])
        self.angle = angle_radians  
        self.draw_car()
        
    def move_forward(self, distance):
        self.position += self.orientation * distance
        self.draw_car()
    
    def move_backward(self, distance):
        self.position -= self.orientation * distance
        self.draw_car()

    def get_distX(self):
        # return self.position[0]
        state.x = self.position[0]
        return state.x
    def get_distY(self):
        # return self.position[1]
        state.y = self.position[1]
        return state.y
    def get_angle(self):
        # return self.angle
        state.theta = self.angle
        return state.theta