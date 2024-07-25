import math
import time
import numpy as np
from ipycanvas import MultiCanvas  # Importing MultiCanvas from ipycanvas for drawing on multiple canvases
from shapely.geometry import Point, Polygon  # For geometric calculations
import ipywidgets as widgets  # For creating interactive widgets
from IPython.display import display  # For displaying widgets in a Jupyter notebook

# This class represents a microphone in the arena with its ID and position.
class Mic:
    def __init__(self, id, position):
        self.id = id
        self.position = position

    # Plot the microphone
    def plot(self, canvas):
        x, y, _ = self.position
        canvas.fill_style = 'blue'  # Set fill color for the microphone
        canvas.fill_circle(x, y, 5)  # Draw filled circle representing the microphone
        canvas.stroke_style = 'black'  # Set stroke color
        canvas.stroke_circle(x, y, 5)  # Draw the outline of the circle
        canvas.fill_style = 'black'  # Set fill color for text
        canvas.fill_text(str(self.id), x + 7, y + 2)  # Draw the microphone ID next to it

# This class represents the arena where the simulation takes place.
class Arena:
    def __init__(self, static_canvas):
        self.static_canvas = static_canvas  # Canvas for static elements like boundaries and obstacles
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

    def draw(self):
        # Draw outer boundaries
        self.static_canvas.fill_style = '#808080'  # Set fill color for outer boundaries
        self.static_canvas.fill_rect(self.outer_boundaries[0], self.outer_boundaries[1],
                                     self.outer_boundaries[2] - self.outer_boundaries[0],
                                     self.outer_boundaries[3] - self.outer_boundaries[1])
        
        # Draw inner boundaries
        self.static_canvas.fill_style = 'white'  # Set fill color for inner boundaries
        self.static_canvas.fill_rect(self.inner_boundaries[0], self.inner_boundaries[1],
                                     self.inner_boundaries[2] - self.inner_boundaries[0],
                                     self.inner_boundaries[3] - self.inner_boundaries[1])
        
        # Draw boundaries
        self.static_canvas.stroke_style = 'red'  # Set stroke color for boundaries
        self.static_canvas.set_line_dash([4, 2])  # Set line dash pattern
        self.static_canvas.stroke_rect(self.boundaries[0], self.boundaries[1],
                                       self.boundaries[2] - self.boundaries[0],
                                       self.boundaries[3] - self.boundaries[1])
        self.static_canvas.set_line_dash([])  # Reset line dash pattern
        
        # Draw obstacles
        self.static_canvas.fill_style = 'salmon'  # Set fill color for obstacles
        self.static_canvas.stroke_style = 'black'  # Set stroke color for obstacles
        for obstacle in self.obstacles:
            self.static_canvas.fill_polygon(obstacle)  # Draw filled polygon for each obstacle
            self.static_canvas.stroke_polygon(obstacle)  # Draw the outline of each obstacle
        
        # Draw waypoints
        self.static_canvas.fill_style = 'red'  # Set fill color for waypoints
        for waypoint in self.waypoints:
            x, y, radius = waypoint
            self.static_canvas.fill_circle(x, y, radius)  # Draw filled circle for each waypoint
            self.static_canvas.stroke_circle(x, y, radius)  # Draw the outline of each waypoint
        
        # Draw microphones
        for mic in self.mics:
            mic.plot(self.static_canvas)  # Plot each microphone on the canvas

    def point_in_polygon(self, x, y, polygon):
        point = Point(x, y)
        poly = Polygon(polygon)
        return point.within(poly)  # Check if point is within the polygon

# Class to handle distance sensors in the car
class DistanceSensors:
    Maxrange = 300
    Minrange = 10
    Aperture = 30 * math.pi / 180
    Zaprange = 40

    def __init__(self, obstacles, offsetL=(20, 15), offsetR=(20, -15)):
        self.obstacles = [Polygon(obstacle) for obstacle in obstacles]  # Convert obstacle points to polygons
        self.offsetL = np.array(offsetL)  # Left sensor offset
        self.offsetR = np.array(offsetR)  # Right sensor offset

    def x_offset(self, x, d, offset):
        dperp = np.array([-d[1], d[0]])  # Perpendicular direction vector
        return x + offset[0] * d + offset[1] * dperp  # Calculate offset position

    def cone(self, x, d):
        dperp = np.array([-d[1], d[0]])  # Perpendicular direction vector
        aperture2 = self.Aperture / 2
        D = self.Maxrange * d * math.cos(aperture2)
        Dperp = self.Maxrange * dperp * math.sin(aperture2)
        y = x + D + Dperp
        z = x + D - Dperp
        return Polygon([x, y, z])

    def distance(self, x, d):
        sensor_cone = self.cone(x, d)  # Get the sensor's cone
        min_distance = self.Maxrange  # Initialize minimum distance
        for obstacle in self.obstacles:
            if sensor_cone.intersects(obstacle):  # Check for intersection with obstacles
                intersection = sensor_cone.intersection(obstacle)
                if intersection.geom_type == 'Polygon':
                    points = list(intersection.exterior.coords)
                else:
                    points = []
                    for geom in intersection.geoms:
                        if geom.geom_type == 'Polygon':
                            points.extend(list(geom.exterior.coords))
                for point in points:
                    dist = np.linalg.norm(np.array(point) - x)  # Calculate distance to intersection point
                    if dist < min_distance:
                        min_distance = dist
        return max(self.Minrange, min_distance)

    def distL(self, x, d):
        x_L = self.x_offset(x, d, self.offsetL)  # Get position for left sensor
        return self.distance(x_L, d)  # Calculate distance for left sensor

    def distR(self, x, d):
        x_R = self.x_offset(x, d, self.offsetR)  # Get position for right sensor
        return self.distance(x_R, d)  # Calculate distance for right sensor

# Class representing the car in the simulation.
class Car:
    B = 20

    def __init__(self, dynamic_canvas, arena, info_text_ids, state):
        self.dynamic_canvas = dynamic_canvas  # Canvas for dynamic elements like the car
        self.arena = arena
        self.info_text_ids = info_text_ids
        self.state = state
        self.position = np.array([state.x, 480 - state.y], dtype=float)  # Adjusted for inversion
        self.orientation = np.array([math.cos(state.theta), -math.sin(state.theta)], dtype=float)
        self.front_wheel_angle = 0
        self.velocity = state.v
        self.angle = state.theta
        self.time = state.last_update
        self.path = []
        self.start_time = time.time()
        self.frame_count = 0
        self.sensors = DistanceSensors(arena.obstacles)  # Initialize sensors with arena obstacles
        self.motor_command = 150
        self.servo_command = 150
        self.draw_car()

    def update_orientation(self, theta):
        self.orientation = np.array([math.cos(theta), -math.sin(theta)], dtype=float)  # Update orientation vector

    def update_front_wheel_angle(self, d_theta):
        if d_theta > 0:
            self.front_wheel_angle = -np.pi / 9  # Turn right (30 degrees)
        elif d_theta < 0:
            self.front_wheel_angle = np.pi / 9  # Turn left (30 degrees)
        else:
            self.front_wheel_angle = 0  # Straight

    # Method to draw the car on the dynamic canvas.
    def draw_car(self):
        # Clear only the dynamic canvas
        self.dynamic_canvas.clear()

        car_length = 34
        car_width = 16
        center_x, center_y = self.position
        dx, dy = self.orientation
        perp_dx, perp_dy = dy, -dx  # Adjusted for inversion

        self.corners = [
            (center_x + 0.5 * car_length * dx + 0.5 * car_width * perp_dx,
             center_y + 0.5 * car_length * dy + 0.5 * car_width * perp_dy),
            (center_x + 0.5 * car_length * dx - 0.5 * car_width * perp_dx,
             center_y + 0.5 * car_length * dy - 0.5 * car_width * perp_dy),
            (center_x - 0.5 * car_length * dx - 0.5 * car_width * perp_dx,
             center_y - 0.5 * car_length * dy - 0.5 * car_width * perp_dy),
            (center_x - 0.5 * car_length * dx + 0.5 * car_width * perp_dx,
             center_y - 0.5 * car_length * dy + 0.5 * car_width * perp_dy)
        ]
        colors = ["red", "green", "black", "orange"]  # Colors for the car's edges

        for i in range(4):
            start_corner = self.corners[i]
            end_corner = self.corners[(i + 1) % 4]
            self.dynamic_canvas.stroke_style = colors[i]  # Set stroke color for each edge
            self.dynamic_canvas.line_width = 2
            self.dynamic_canvas.stroke_line(start_corner[0], start_corner[1], end_corner[0], end_corner[1])  # Draw each edge

        wheel_length = 8
        wheel_width = 4
        wheel_color = 'blue'
        wheel_offset = 4

        # Adjust front wheel angle based on steering input
        cos_a, sin_a = math.cos(self.front_wheel_angle), math.sin(self.front_wheel_angle)
        front_wheel_dx, front_wheel_dy = cos_a * dx - sin_a * dy, sin_a * dx + cos_a * dy

        self.front_wheels = [
            np.array(self.corners[0]) + wheel_offset * np.array([perp_dx, perp_dy]),
            np.array(self.corners[1]) + wheel_offset * np.array([-perp_dx, -perp_dy])
        ]
        for corner in self.front_wheels:
            wheel_start = corner
            wheel_end = wheel_start + wheel_length * np.array([front_wheel_dx, front_wheel_dy])
            self.dynamic_canvas.stroke_style = wheel_color  # Set stroke color for wheels
            self.dynamic_canvas.line_width = wheel_width
            self.dynamic_canvas.stroke_line(wheel_start[0], wheel_start[1], wheel_end[0], wheel_end[1])  # Draw front wheels

        self.back_wheels = [
            np.array(self.corners[2]) + wheel_offset * np.array([-perp_dx, -perp_dy]),
            np.array(self.corners[3]) + wheel_offset * np.array([perp_dx, perp_dy])
        ]
        for corner in self.back_wheels:
            wheel_start = corner
            wheel_end = wheel_start - wheel_length * np.array([dx, dy])
            self.dynamic_canvas.stroke_style = wheel_color  # Set stroke color for wheels
            self.dynamic_canvas.line_width = wheel_width
            self.dynamic_canvas.stroke_line(wheel_start[0], wheel_start[1], wheel_end[0], wheel_end[1])  # Draw back wheels

        self.update_info()
        self.update_motor_servo(self.motor_command, self.servo_command)

    # Draw the path that the car has traveled.
    def draw_path(self):
        self.path.append((self.position[0], self.position[1]))  # Add current position to the path
        if len(self.path) > 1:
            self.dynamic_canvas.stroke_style = '#D3D3D3'  # Set stroke color for the path [widnows require hexadecimal for grey color]
            self.dynamic_canvas.line_width = 2
            self.dynamic_canvas.stroke_lines(self.path)  # Draw the path as a continuous line

    # Update the car's information display.
    def update_info(self):
        elapsed_time = time.time() - self.start_time
        fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
        self.frame_count += 1
        distL = self.sensors.distL(self.position, self.orientation)
        distR = self.sensors.distR(self.position, self.orientation)
        info_texts = [
            f"X: {self.position[0]:.2f}",
            f"Y: {480.0 - abs(self.position[1]):.2f}",
            f"v: {self.velocity:.2f}",
            f"angle: {math.degrees(self.angle):.2f}",
            f"FPS: {fps:.2f}",
            f"distL: {distL:.2f}",
            f"distR: {distR:.2f}"
        ]
        self.dynamic_canvas.font = "7px Helvetica"
        self.dynamic_canvas.clear_rect(400, 0, 120, 100)  # Clear the area before redrawing
        for i, text in enumerate(info_texts):
            self.dynamic_canvas.fill_text(text, 470, 20 + i * 12)  # Draw each line of info text

    # Update the motor and servo commands displayed on the canvas.
    def update_motor_servo(self, motor_command, servo_command):
        self.dynamic_canvas.font = "12px Arial"
        self.dynamic_canvas.fill_style = "black"
        self.dynamic_canvas.clear_rect(0, 480 - 45, 100, 45)  # Clear the area before redrawing
        self.dynamic_canvas.fill_text(f"M{motor_command}", 30, 480 - 15)  # Display motor command
        self.dynamic_canvas.fill_text(f"D{servo_command}", 30, 480)  # Display servo command

    # Check if the car has collided with the arena boundaries or obstacles.
    def check_collision(self):
        min_x, min_y, max_x, max_y = self.arena.boundaries
        for wheel in self.front_wheels + self.back_wheels:
            x, y = wheel
            if not (min_x < x < max_x and min_y < y < max_y):  # Check if wheel is out of boundaries
                return True
            for obstacle in self.arena.obstacles:
                if self.arena.point_in_polygon(x, y, obstacle):  # Check if wheel is within an obstacle
                    return True
        return False

# GUI class
class GUI:
    def __init__(self, state, motor_command, servo_command):
        self.canvas_width = 525
        self.canvas_height = 525
        self.arena_width = 480
        self.arena_height = 480
        self.offset_x = (self.canvas_width - self.arena_width) // 2
        self.offset_y = (self.canvas_height - self.arena_height) // 2
        
        # MultiCanvas with two layers: one for static elements and one for dynamic elements
        self.canvas = MultiCanvas(2, width=self.canvas_width, height=self.canvas_height, layout=widgets.Layout(width=f'{self.canvas_width}px', height=f'{self.canvas_height}px'))
        self.static_canvas = self.canvas[0]  # Canvas for static elements
        self.dynamic_canvas = self.canvas[1]  # Canvas for dynamic elements
        self.info_labels = list(range(7))  # Labels for displaying car info
        self.motor_label = widgets.Label(value=f"M{motor_command}", layout=widgets.Layout(width='80px'))
        self.servo_label = widgets.Label(value=f"D{servo_command}", layout=widgets.Layout(width='80px'))
        self.state = state
        self.motor_command = motor_command
        self.servo_command = servo_command
        self.arena = Arena(self.static_canvas)  # Initialize arena with static canvas
        self.car = Car(self.dynamic_canvas, self.arena, self.info_labels, self.state)  # Initialize car with dynamic canvas
        self.arena.draw()  # Draw static elements on the static canvas
        self.prev_theta = self.state.theta
        self.simulation_running = True

    def update(self):
        if not self.simulation_running:
            return
        self.car.position = np.array([self.state.x, 480 - self.state.y], dtype=float)  # Update car's position
        self.car.update_orientation(self.state.theta)  # Update car's orientation

        d_theta = self.state.theta - self.prev_theta
        self.car.update_front_wheel_angle(d_theta)  # Update front wheel angle based on change in orientation

        self.car.velocity = self.state.v  # Update car's velocity
        self.car.angle = self.state.theta  # Update car's angle
        self.car.time = self.state.last_update  # Update car's last update time
        self.car.motor_command = self.motor_command  # Update motor command
        self.car.servo_command = self.servo_command  # Update servo command
        self.car.draw_car()  # Redraw the car on the dynamic canvas
        self.car.draw_path()  # Draw the car's path on the dynamic canvas
        
        if not self.car.check_collision():  # Check for collision before drawing the car
            self.car.draw_car()  # Redraw the car if no collision
            self.car.draw_path()  # Redraw the path if no collision
        else:
            self.simulation_running = False  # Stop simulation if collision detected
            self.dynamic_canvas.fill_style = "red"
            self.dynamic_canvas.fill_text("Collision Detected!", self.dynamic_canvas.width / 2, self.dynamic_canvas.height / 2)  # Display collision message

        self.prev_theta = self.state.theta  # Update previous theta

    def display(self):
        display(widgets.VBox([self.canvas]))  # Display the canvas within a VBox widget

    def __del__(self):
        self.simulation_running = False

