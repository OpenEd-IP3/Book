import time
import numpy as np
from KITT_Simulator.sharedState import SharedState
import logging

class Dynamics:
    def __init__(self, start_state):
        """Initializes the Dynamics class with the start state and parameters."""
        # logging.basicConfig(level=logging.WARNING)
        logging.basicConfig(filename='dynamicsSimulator.log', level=logging.DEBUG)
        logging.info("Starting Dynamics")
        self.start_time = time.time()
        self.state = start_state
        
        self.mass = 5.6  # Mass of the car in kg
        self.L = 1  # Length of the car in cm
        self.T = 1  # Track width in cm

        self.F = {}
        self.b = 5
        self.R = {}
        logging.debug("Reading Motor and Servo Parameters")
        with open("KITT_Simulator/motor_parameters.txt", "r") as f:
            for line in f:
                line = line.split(sep=",")
                self.F[int(line[0])] = float(line[1])
        with open("KITT_Simulator/servo_parameters.txt", "r") as f:
            for line in f:
                line = line.split(sep=",")
                self.R[int(line[0])] = float(line[1])
        self.motor_command = 150
        self.servo_command = 150
        logging.debug("Initial State Update")
        self.update_state()
        logging.debug("Completed Initial State Update")

    def update_state(self):
        """Updates the state of the car based on the motor and servo commands."""
        logging.debug(f"Updating State using {self.state.motor_command} and {self.state.servo_command}")

        # Get the parameters for the motor and servo commands
        F, b, R, direction = self.map_command(self.motor_command, self.servo_command)  # F = motor force, b = drag coefficient, R = turn radius, direction = left or right turn

        logging.debug(f"Motor Force: {F}, Drag Coefficient: {b}, Turn Radius: {R}, Direction: {direction}")

        # Calculate time since last update
        update_time = time.time()
        delta_t = update_time - self.state.last_update
        self.state.last_update = update_time

        # Calculate how far the car moves during delta_t
        logging.debug(f"Delta Time: {delta_t}")
        arc_length = self.calculate_arc_length(F, b, delta_t)
        logging.debug(f"Arc Length: {arc_length}")
        self.arc_length = arc_length
        self.update_position(arc_length, R, direction)
        logging.debug(f"Updated Position: {self.state.x}, {self.state.y}, {self.state.theta}")

        self.motor_command = self.state.motor_command
        self.servo_command = self.state.servo_command

    def map_command(self, motor_command, servo_command):
        """Converts a command into motor force and turn radius."""
        try:
            motor_force = self.F.get(motor_command)
            turn_radius = self.R.get(servo_command)
        except:
            motor_force = 0
            turn_radius = 0
            logging.error(f"Invalid Motor or Servo Command: M{motor_command}, D{servo_command}")
        direction = "Left" if float(servo_command) > 150 else "Right"
        logging.debug(f"Mapped Command: Motor Force: {motor_force}, Turn Radius: {turn_radius}, Direction: {direction}")
        return motor_force, self.b, turn_radius, direction

    def calculate_arc_length(self, F, b, delta_t):
        """Calculates the arc length the car moves during delta_t."""
        arc_length = (F)/(b)*delta_t + (F*self.mass-self.mass*b*self.state.v)/(b**2)*np.exp(-(b)/(self.mass)*delta_t) - (F*self.mass-self.mass*b*self.state.v)/(b**2)
        # Calculate the new velocity of the car
        self.state.v = (F)/(b) + (self.state.v - (F)/(b))*(np.exp(-(b)/(self.mass)*delta_t))
        logging.debug(f"Calculated Arc Length: {arc_length}, New Velocity: {self.state.v}")
        return arc_length

    def update_position(self, arc_length, R, direction):
        """Updates the position of the car based on the arc length and turn radius."""
        x0 = self.state.x
        y0 = self.state.y
        theta0 = self.state.theta
        logging.debug(f"Initial Position: x0: {x0}, y0: {y0}, theta0: {theta0}")

        if R != 0:
            arc_angle = arc_length / (R)  # angle between start and end of path along the circle
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
        logging.debug(f"Updated Position: x: {x}, y: {y}, theta: {theta}")