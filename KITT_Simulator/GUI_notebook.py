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
    
class Car:
    def __init__(self, canvas, state, arena):
        self.canvas = canvas
        self.state = state
        self.arena = arena
        self.position = np.array([state.x, 480 - state.y], dtype=float)
        self.orientation = np.array([math.cos(state.theta), -math.sin(state.theta)], dtype=float)
        self.front_wheel_angle = 0
        self.prev_position = self.position.copy()
        self.car_length = 34
        self.car_width = 16
        self.wheel_length = 8
        self.wheel_width = 4
        self.wheel_offset = 4
        self.clear_margin = 2

        # Initialize previous positions as empty lists or None
        self.prev_corners = None
        self.prev_front_wheels = None
        self.prev_back_wheels = None

    def clear_behind(self):
        """Clears the area behind the car, including wheels, and redraws any affected obstacles or boundaries."""
        if self.prev_corners and self.prev_front_wheels and self.prev_back_wheels:

            all_prev_points = self.prev_corners + [
                p[0] for p in self.prev_front_wheels + self.prev_back_wheels
            ] + [
                p[1] for p in self.prev_front_wheels + self.prev_back_wheels
            ]

            min_x = min(p[0] for p in all_prev_points) - self.clear_margin
            max_x = max(p[0] for p in all_prev_points) + self.clear_margin
            min_y = min(p[1] for p in all_prev_points) - self.clear_margin
            max_y = max(p[1] for p in all_prev_points) + self.clear_margin

            self.canvas.clear_rect(min_x, min_y, max_x - min_x, max_y - min_y)

            self.redraw_affected_areas(min_x, min_y, max_x, max_y)

    def redraw_affected_areas(self, min_x, min_y, max_x, max_y):
        """redraws obstacles and boundaries that might have been cleared. this is made due to the car bounding box size"""
        for obstacle in self.arena.obstacles:
            if self.rect_intersects_polygon(min_x, min_y, max_x, max_y, obstacle):
                self.canvas.fill_style = 'salmon'
                self.canvas.stroke_style = 'black'
                self.canvas.fill_polygon(obstacle)
                self.canvas.stroke_polygon(obstacle)

        if self.rect_intersects_rect(min_x, min_y, max_x, max_y, *self.arena.boundaries):
            self.canvas.stroke_style = 'red'
            self.canvas.set_line_dash([4, 2])
            self.canvas.stroke_rect(self.arena.boundaries[0], self.arena.boundaries[1],
                                    self.arena.boundaries[2] - self.arena.boundaries[0],
                                    self.arena.boundaries[3] - self.arena.boundaries[1])
            self.canvas.set_line_dash([])

        for mic in self.arena.mics:
            if min_x <= mic.position[0] <= max_x and min_y <= mic.position[1] <= max_y:
                mic.plot(self.canvas)


    def rect_intersects_polygon(self, min_x, min_y, max_x, max_y, polygon):
        """check if a rectangle intersects with a obstacle"""
        poly = Polygon(polygon)
        rect = Polygon([(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)])
        return poly.intersects(rect)

    def rect_intersects_rect(self, min_x, min_y, max_x, max_y, bx1, by1, bx2, by2):
        """check if a rectangle intersects another rect due to clearing."""
        return not (bx1 > max_x or bx2 < min_x or by1 > max_y or by2 < min_y)

    def update_orientation(self, theta):
        """update the car's orientation based on the new angle theta."""
        self.orientation = np.array([math.cos(theta), -math.sin(theta)], dtype=float)

    def draw_car(self):
        
        self.clear_behind() # Clear only the previous car position

        car_length = self.car_length
        car_width = self.car_width
        wheel_length = self.wheel_length
        wheel_width = self.wheel_width
        wheel_offset = self.wheel_offset

        center_x, center_y = self.position
        dx, dy = self.orientation
        perp_dx, perp_dy = dy, -dx

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

        cos_a, sin_a = math.cos(self.front_wheel_angle), math.sin(self.front_wheel_angle)
        front_wheel_dx, front_wheel_dy = cos_a * dx - sin_a * dy, sin_a * dx + cos_a * dy

        self.front_wheels = [
            (np.array(self.corners[0]) + wheel_offset * np.array([perp_dx, perp_dy]),
             np.array(self.corners[0]) + wheel_offset * np.array([perp_dx, perp_dy]) + wheel_length * np.array([front_wheel_dx, front_wheel_dy])),
            (np.array(self.corners[1]) + wheel_offset * np.array([-perp_dx, -perp_dy]),
             np.array(self.corners[1]) + wheel_offset * np.array([-perp_dx, -perp_dy]) + wheel_length * np.array([front_wheel_dx, front_wheel_dy]))
        ]

        self.back_wheels = [
            (np.array(self.corners[2]) + wheel_offset * np.array([-perp_dx, -perp_dy]),
             np.array(self.corners[2]) + wheel_offset * np.array([-perp_dx, -perp_dy]) - wheel_length * np.array([dx, dy])),
            (np.array(self.corners[3]) + wheel_offset * np.array([perp_dx, perp_dy]),
             np.array(self.corners[3]) + wheel_offset * np.array([perp_dx, perp_dy]) - wheel_length * np.array([dx, dy]))
        ]

        # Draw the car body
        colors = ["red", "green", "black", "orange"]
        for i in range(4):
            start_corner = self.corners[i]
            end_corner = self.corners[(i + 1) % 4]
            self.canvas.stroke_style = colors[i]
            self.canvas.line_width = 2
            self.canvas.stroke_line(start_corner[0], start_corner[1], end_corner[0], end_corner[1])

        # Draw the wheels
        self.canvas.stroke_style = 'blue'
        self.canvas.line_width = wheel_width
        for wheel_start, wheel_end in self.front_wheels + self.back_wheels:
            self.canvas.stroke_line(wheel_start[0], wheel_start[1], wheel_end[0], wheel_end[1])


        self.prev_position = self.position.copy()   # Update previous positions for the next frame
        self.prev_corners = self.corners
        self.prev_front_wheels = self.front_wheels
        self.prev_back_wheels = self.back_wheels

    def check_collision(self):
        min_x, min_y, max_x, max_y = self.arena.boundaries
        for wheel in self.front_wheels + self.back_wheels:
            x, y = wheel[0]
            if not (min_x < x < max_x and min_y < y < max_y):
                return True
            for obstacle in self.arena.obstacles:
                if self.arena.point_in_polygon(x, y, obstacle):
                    return True
        return False
    
class GUI:
    def __init__(self, state, motor_command, servo_command):
        self.canvas_width = 525
        self.canvas_height = 525
        self.arena_width = 480
        self.arena_height = 480
        self.offset_x = (self.canvas_width - self.arena_width) // 2
        self.offset_y = (self.canvas_height - self.arena_height) // 2
        
        self.canvas = Canvas(width=self.canvas_width, height=self.canvas_height, layout=widgets.Layout(width=f'{self.canvas_width}px', height=f'{self.canvas_height}px'))
        self.info_labels = list(range(7))

        self.state = state
        self.motor_command = motor_command
        self.servo_command = servo_command
        self.arena = Arena(self.canvas)
        self.arena.draw()
        self.car = Car(self.canvas, self.state, self.arena)
        self.prev_theta = self.state.theta
        self.simulation_running = True

    def update(self):
        if not self.simulation_running:
            return

        self.car.position = np.array([self.state.x, 480 - self.state.y], dtype=float)
        self.car.update_orientation(self.state.theta)

        self.car.draw_car()

        if self.car.check_collision():
            self.simulation_running = False
            self.canvas.fill_style = "red"
            self.canvas.fill_text("Collision Detected!", self.canvas.width / 2, self.canvas.height / 2)

        self.prev_theta = self.state.theta

    def display(self):
        # Ensure the canvas is displayed in the notebook
        display(self.canvas)

    def run(self):
        self.simulation_running = True
        while self.simulation_running:
            self.update()
            time.sleep(0.033)  # 30 FPS

    def stop(self):
        self.simulation_running = False

    def __del__(self):
        self.simulation_running = False