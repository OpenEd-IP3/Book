import tkinter as tk
import math

class GUI:
    """GUI class to display the car's position and orientation."""

    def __init__(self, state, motor_command, servo_command):
        self.state = state
        self.motor_command = motor_command
        self.servo_command = servo_command

        self.root = tk.Tk()
        self.root.title("Car Simulator")

        self.canvas_width = 500
        self.canvas_height = 500

        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()

        self.car_length = 40
        self.car_width = 20

        # Create the car as a polygon
        self.car = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, fill="blue")

        self.update_interval = 50  # Update every 50ms
        self.root.after(self.update_interval, self.update)

    def update(self):
        """Updates the car's position on the canvas."""
        with self.state._lock:
            x = self.state.x
            y = self.state.y
            theta = self.state.theta

        # Convert car position from cm to pixels and adjust for canvas scaling
        canvas_x = x * (self.canvas_width / 480)  # Assuming world is 480cm wide
        canvas_y = self.canvas_height - y * (self.canvas_height / 480)  # Assuming world is 480cm tall

        # Calculate the car's corner points based on orientation
        half_length = self.car_length / 2
        half_width = self.car_width / 2

        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        x1 = canvas_x - half_length * cos_theta + half_width * sin_theta
        y1 = canvas_y - half_length * sin_theta - half_width * cos_theta

        x2 = canvas_x + half_length * cos_theta + half_width * sin_theta
        y2 = canvas_y + half_length * sin_theta - half_width * cos_theta

        x3 = canvas_x + half_length * cos_theta - half_width * sin_theta
        y3 = canvas_y + half_length * sin_theta + half_width * cos_theta

        x4 = canvas_x - half_length * cos_theta - half_width * sin_theta
        y4 = canvas_y - half_length * sin_theta + half_width * cos_theta

        # Update the car's position on the canvas
        self.canvas.coords(self.car, x1, y1, x2, y2, x3, y3, x4, y4)

        # Schedule the next update
        self.root.after(self.update_interval, self.update)

    def safe_update(self):
        """Safely update the GUI from another thread."""
        self.root.after(0, self.update)

    def display(self):
        """Runs the Tkinter main loop."""
        self.root.mainloop()