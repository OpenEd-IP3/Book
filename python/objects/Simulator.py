import numpy as np
import math
from shapely.geometry import Polygon, Point, LineString
import tkinter as tk
import numpy as np
import math
import time
from shapely.geometry import Polygon, Point
import numpy as np
import random

class Mic:
    def __init__(self, index, location, samplerate=40000, easymode=False):
        self.index = index
        self.location = np.array(location)
        self.samplerate = samplerate
        self.noiselevel = 0.001 if easymode else 0.012
        self.maxlevel = 1
        self.loudspeaker = self.load_loudspeaker_response()

    def load_loudspeaker_response(self):
        # Simulate loading and resampling
        Fs_original = 48000
        impulse_response = np.random.randn(Fs_original)  # Example impulse response
        return self.resample(impulse_response, self.samplerate, Fs_original)

    def resample(self, signal, new_rate, old_rate):
        duration = len(signal) / old_rate
        new_length = int(duration * new_rate)
        return np.interp(np.linspace(0, duration, new_length), np.linspace(0, duration, len(signal)), signal)

    def plot(self, canvas):
            x, y = self.location[:2]
            mic_radius = 5
            canvas.create_oval(x - mic_radius, y - mic_radius, x + mic_radius, y + mic_radius, fill='black', tags="mic")

    def receive(self, beacon_location, message):
        Fs = self.samplerate
        h_room = self.room_impulse_response(beacon_location)
        h_loud = self.loudspeaker

        N = len(message)
        s = self.circular_convolution(h_room, message, N)
        s = self.circular_convolution(h_loud, s, N)
        s = s + self.noiselevel * np.random.randn(N)
        s = np.clip(s, -self.maxlevel, self.maxlevel)
        return s

    def room_impulse_response(self, beacon_location):
        distance = np.linalg.norm(self.location - beacon_location)
        tau = distance / 343  # Speed of sound in cm/s
        n = int(round(tau * self.samplerate))
        h = np.zeros(n)
        h[-1] = 1 / distance
        return h

    def circular_convolution(self, h, x, N):
        return np.real(np.fft.ifft(np.fft.fft(h, N) * np.fft.fft(x, N)))

    def listen(self, beacon_location, message):
        signal = self.receive(beacon_location, message)
        # Simulate
        print(f"Listening to microphone {self.index}")
        return signal

class DistanceSensors:
    Maxrange = 300  # max cm
    Minrange = 10   # min cm
    Aperture = 30 * math.pi / 180  # opening angle of sensor (rad)
    Zaprange = 40  # cm; range of zap to destroy object

    def __init__(self, obstacles, offsetL=(20, 15), offsetR=(20, -15)):
        self.obstacles = [Polygon(obstacle) for obstacle in obstacles]
        self.offsetL = np.array(offsetL)
        self.offsetR = np.array(offsetR)

    def x_offset(self, x, d, offset):
        dperp = np.array([-d[1], d[0]])
        return x + offset[0] * d + offset[1] * dperp

    def cone(self, x, d):
        dperp = np.array([-d[1], d[0]])
        aperture2 = self.Aperture / 2
        D = self.Maxrange * d * math.cos(aperture2)
        Dperp = self.Maxrange * dperp * math.sin(aperture2)
        y = x + D + Dperp
        z = x + D - Dperp
        return Polygon([x, y, z])

    def distance(self, x, d):
        sensor_cone = self.cone(x, d)
        min_distance = self.Maxrange

        for obstacle in self.obstacles:
            if sensor_cone.intersects(obstacle):
                intersection = sensor_cone.intersection(obstacle)
                if intersection.geom_type == 'Polygon':
                    points = list(intersection.exterior.coords)
                else:  # MultiPolygon or GeometryCollection
                    points = []
                    for geom in intersection.geoms:
                        if geom.geom_type == 'Polygon':
                            points.extend(list(geom.exterior.coords))

                for point in points:
                    dist = np.linalg.norm(np.array(point) - x)
                    if dist < min_distance:
                        min_distance = dist

        return max(self.Minrange, min_distance)

    def distL(self, x, d):
        x_L = self.x_offset(x, d, self.offsetL)
        return self.distance(x_L, d)

    def distR(self, x, d):
        x_R = self.x_offset(x, d, self.offsetR)
        return self.distance(x_R, d)

class Arena:
    def __init__(self, canvas):
        self.canvas = canvas
        self.obstacles = [
            [(200, 200), (260, 200), (260, 240), (230, 240)],
            [(350, 200), (410, 200), (410, 240), (380, 240)]
        ]
        self.waypoints = [
            (400, 400, 420, 420)
        ]
        self.boundaries = [50, 50, 550, 550]
        self.inner_boundaries = [50, 50, 550, 550]  # Original boundary coordinates
        self.outer_boundaries = [40, 40, 560, 560]  # New boundary coordinates
        self.mic_positions = [
                    (50, 50, 0),
                    (550, 50, 0),
                    (50, 550, 0),
                    (550, 550, 0)
                ]
        self.mics = [Mic(i+1, pos) for i, pos in enumerate(self.mic_positions)]
    def draw(self):
        self.canvas.create_rectangle(*self.outer_boundaries, outline="black", fill="grey", tags="arena")
        self.canvas.create_rectangle(*self.inner_boundaries, outline="black", fill="white", tags="arena")
        self.canvas.create_rectangle(*self.boundaries, dash=(4, 2), outline="red", tags="arena")
        for obstacle in self.obstacles:
            self.canvas.create_polygon(obstacle, fill="salmon", outline="black", tags="arena")
        for waypoint in self.waypoints:
            self.canvas.create_oval(waypoint, fill="red", outline="black", tags="arena")
        for mic in self.mics:
            mic.plot(self.canvas)
    def check_collision(self, wheels):
        min_x, min_y, max_x, max_y = self.boundaries
        for wheel in wheels:
            x, y = wheel
            if not (min_x < x < max_x and min_y < y < max_y):
                return True
            for obstacle in self.obstacles:
                if self.point_in_polygon(x, y, obstacle):
                    return True
        return False

    def point_in_polygon(self, x, y, polygon):
        point = Point(x, y)
        poly = Polygon(polygon)
        return point.within(poly)

class Car:
    B = 20  # distance from center of car to front wheels (cm)

    def __init__(self, canvas, arena, info_text_ids):
        self.canvas = canvas
        self.arena = arena
        self.info_text_ids = info_text_ids
        self.position = np.array([90, 520], dtype=float)
        self.orientation = np.array([0, -1], dtype=float)
        self.velocity = 0  # initial velocity
        self.angle = 0  # steering angle
        self.time = time.time()  # current time
        self.path = []  # to store the path of the car
        self.gui_to_real_factor = 7 / 10  # Example conversion factor
        self.real_position = np.array([0, 0], dtype=float)  # Real-world position starting at (0, 0)
        self.start_time = time.time()
        self.frame_count = 0
        self.sensors = DistanceSensors(arena.obstacles)
        self.draw_car()

    def draw_car(self):
        self.canvas.delete("car")
        car_length = 42  # length
        car_width = 20  # width

        center_x, center_y = self.position
        dx, dy = self.orientation
        perp_dx, perp_dy = -dy, dx

        # Coordinates of each corner
        self.corners = [
            (center_x + 0.5 * car_length * dx + 0.5 * car_width * -dy,
             center_y + 0.5 * car_length * dy + 0.5 * car_width * dx),
            (center_x + 0.5 * car_length * dx - 0.5 * car_width * -dy,
             center_y + 0.5 * car_length * dy - 0.5 * car_width * dx),
            (center_x - 0.5 * car_length * dx - 0.5 * car_width * -dy,
             center_y - 0.5 * car_length * dy - 0.5 * car_width * dx),
            (center_x - 0.5 * car_length * dx + 0.5 * car_width * -dy,
             center_y - 0.5 * car_length * dy + 0.5 * car_width * dx)
        ]
        colors = ["red", "green", "black", "orange"]

        # Draw car border with different colors
        for i in range(4):
            start_corner = self.corners[i]
            end_corner = self.corners[(i + 1) % 4]
            self.canvas.create_line(start_corner[0], start_corner[1], end_corner[0], end_corner[1],
                                    fill=colors[i], width=2, tags="car")
        #self.canvas.create_polygon(self.corners, fill='', outline='black', tags="car")
        wheel_length = 10
        wheel_width = 3
        wheel_color = 'blue'
        wheel_offset = 5

        # Front wheels
        rot_angle = self.angle
        cos_a, sin_a = math.cos(rot_angle), math.sin(rot_angle)
        self.front_wheels = [
            np.array(self.corners[0]) + wheel_offset * np.array([perp_dx, perp_dy]),  # f left
            np.array(self.corners[1]) + wheel_offset * np.array([-perp_dx, -perp_dy])   # f right
        ]
        for corner in self.front_wheels:
            wheel_start = corner
            wheel_end = wheel_start + wheel_length * np.array([cos_a * dx - sin_a * dy, sin_a * dx + cos_a * dy])
            self.canvas.create_line(wheel_start[0], wheel_start[1], wheel_end[0], wheel_end[1],
                                    width=wheel_width, fill=wheel_color, tags="car")

        # Back wheels
        self.back_wheels = [
            np.array(self.corners[2]) + wheel_offset * np.array([-perp_dx, -perp_dy]),  # r right
            np.array(self.corners[3]) + wheel_offset * np.array([perp_dx, perp_dy])   # r left
        ]
        for corner in self.back_wheels:
            wheel_start = corner
            wheel_end = wheel_start - wheel_length * np.array([dx, dy])
            self.canvas.create_line(wheel_start[0], wheel_start[1], wheel_end[0], wheel_end[1],
                                    width=wheel_width, fill=wheel_color, tags="car")

        # Update real position based on GUI position
        self.real_position = (self.position - np.array([90, 520])) * self.gui_to_real_factor
        self.update_info()

    def update_orientation(self, angle_degrees):
        angle_radians = math.radians(angle_degrees)
        new_orientation = np.array([
            math.cos(angle_radians) * self.orientation[0] - math.sin(angle_radians) * self.orientation[1],
            math.sin(angle_radians) * self.orientation[0] + math.cos(angle_radians) * self.orientation[1]
        ])
        self.orientation = new_orientation / np.linalg.norm(new_orientation)
        self.angle += angle_radians
        self.draw_car()

    def move_forward(self, distance):
        self.update_position(distance)
        self.draw_car()

    def move_backward(self, distance):
        self.update_position(-distance)
        self.draw_car()

    def update_position(self, distance):
        current_time = time.time()
        dt = current_time - self.time
        self.time = current_time
        self.position = self.position + (self.velocity * self.orientation * dt).astype(float)

        # Car will travel a distance over a circle segment
        if self.angle != 0:
            R = self.B / math.sin(self.angle)
            theta = distance / R
            rotation_matrix = np.array([
                [math.cos(theta), -math.sin(theta)],
                [math.sin(theta), math.cos(theta)]
            ])
            self.orientation = rotation_matrix.dot(self.orientation)
            perp_orientation = np.array([-self.orientation[1], self.orientation[0]])
            center = self.position + R * perp_orientation
            self.position = center + rotation_matrix.dot(self.position - center)
        else:
            self.position += distance * self.orientation

    def move_and_trace(self, velocity, angle_degrees):
        self.velocity = velocity
        self.angle = math.radians(angle_degrees)
        self.time = time.time()  # Reset time to avoid large dt in the first update

        while True:
            if self.arena.check_collision(self.front_wheels + self.back_wheels):
                print("Collision detected! Stopping simulation.")
                break
            self.update_position(self.velocity * 0.01)  # Update position incrementally
            self.path.append(self.position.copy())
            self.draw_path()
            self.draw_car()
            self.canvas.update()
            self.frame_count += 1
            time.sleep(0.01)  # Add a short delay for smoother animation

    def draw_path(self):
        for pos in self.path:
            self.canvas.create_oval(pos[0] - 2, pos[1] - 2, pos[0] + 2, pos[1] + 2, fill='blue')

    def update_info(self):
        elapsed_time = time.time() - self.start_time
        fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
        distL = self.sensors.distL(self.position, self.orientation)
        distR = self.sensors.distR(self.position, self.orientation)
        info_texts = [
            f"X: {self.real_position[0]:.2f}",
            f"Y: {abs(self.real_position[1]):.2f}",  # Display y as positive
            f"v: {self.velocity:.2f}",
            f"angle: {math.degrees(self.angle):.2f}",
            f"FPS: {fps:.2f}",
            f"distL: {distL:.2f}",
            f"distR: {distR:.2f}"
        ]
        # for text_id, text in zip(self.info_text_ids, info_texts):
        #     self.canvas.itemconfig(text_id, text=text)
        for text_id, text in zip(self.info_text_ids, info_texts):
            #print(f"Updating text_id {text_id} with text: {text}")  # Debug print
            self.canvas.itemconfig(text_id, text=text, fill='black')
class update_GUI:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=600, height=600)
        self.canvas.pack()
        self.info_labels = [self.canvas.create_text(540, 60 + i * 12, anchor='e', font=("Helvetica", 7), text="") for i in range(7)]

        self.arena = Arena(self.canvas)

        self.car = Car(self.canvas, self.arena, self.info_labels)
        self.arena.draw()
        self.car.draw_car()
        for label in self.info_labels:
            self.canvas.tag_raise(label)
        self.master.after(1000, self.start_simulation)

    def start_simulation(self):
        self.car.move_and_trace(velocity=10, angle_degrees=25)

if __name__ == "__main__":
    root = tk.Tk()
    sim = update_GUI(root)
    root.mainloop()
