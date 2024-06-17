from dataclasses import dataclass
import time
import numpy as np
import matplotlib.pyplot as plt

@dataclass
class state:
    x: float # x position in cm
    y: float # y position in cm
    theta: float # angle in radians
    v: float # velocity in cm/s
    last_update: float = 0

class Dynamics:
    def __init__(self, start_state):
        self.start_time = time.time()
        self.state = start_state
        
        self.mass = 5.6 # Mass of the car in kg
        self.L = 1 # Length of the car in cm
        self.T = 1 # Track width in cm

        self.F = {}
        self.b = 5
        self.R = {}
        with open("motor_parameters.txt", "r") as f:
                f.__next__()
                for line in f:
                    line = line.split(sep=",")
                    self.F[line[0]] = float(line[1])
        with open("servo_parameters.txt", "r") as f:
            f.__next__()
            for line in f:
                line = line.split(sep=",")
                self.R[line[0]] = float(line[1])

        self.motor_command = "150"
        self.servo_command = "150"
        self.update_state("150", "150")

    def update_state(self, motor_command, servo_command):
        # Get the parameters for the motor and servo commands
        F, b, R, direction = self.map_command(self.motor_command, self.servo_command) # F = motor force, b = drag coefficient, R = turn radius, direction = left or right turn

        # Calculate time since last update
        update_time = time.time()
        delta_t = update_time - self.state.last_update
        self.state.last_update = update_time

        # Calculate how far the car moves during delta_t
        arc_length = self.calculate_arc_length(F, b, delta_t)
        self.arc_length = arc_length
        self.update_position(arc_length, R, direction)

        self.motor_command = motor_command
        self.servo_command = servo_command

    def map_command(self, motor_command, servo_command):
        return self.F[motor_command], self.b[motor_command], self.R[servo_command], "Left" if float(servo_command[1:]) < 150 else "Right"

    def calculate_arc_length(self, F, b, delta_t):
        # Calculate the arc length the car moves during delta_t
        arc_length = (F)/(b)*delta_t + (F*self.mass-self.mass*b*self.state.v)/(b**2)*np.exp(-(b)/(self.mass)*delta_t) - (F*self.mass-self.mass*b*self.state.v)/(b**2)
        # Calculate the new velocity of the car
        self.state.v = (F)/(b) + (self.state.v - (F)/(b))*(np.exp(-(b)/(self.mass)*delta_t))
        return arc_length

    def update_position(self, arc_length, R, direction):
        x0 = self.state.x
        y0 = self.state.y
        theta0 = self.state.theta
        if R != 0:
            arc_angle = arc_length / (R) # angle between start and end of path along the circle
            delta_x = R - R*np.cos(arc_angle)
            delta_y = R*np.sin(arc_angle)
            if direction == 'Left':
                delta_x = -delta_x
                arc_angle = -arc_angle
            x = x0 + delta_x*np.cos(theta0 - np.pi/2) + delta_y*np.cos(theta0)
            y = y0 + delta_x*np.sin(theta0 - np.pi/2) + delta_y*np.sin(theta0)
            theta = theta0 - arc_angle
        else:
            x = x0 + arc_length*np.cos(theta0)
            y = y0 + arc_length*np.sin(theta0)
            theta = theta0
        if theta < -np.pi:
            theta += 2*np.pi
        if theta > np.pi:
            theta -= 2*np.pi

        # Update the state
        self.state.x = x
        self.state.y = y
        self.state.theta = theta
