from dataclasses import dataclass
import threading
import numpy as np
import time

@dataclass
class State:
    """Class to represent the current state of the car."""
    x: float  # x position in cm
    y: float  # y position in cm
    theta: float  # angle in radians
    v: float = 0  # velocity in cm/s
    last_update: float = time.time()  # time since last position compute in ms
    motor_command: int = 150  # last received motor command
    servo_command: int = 150  # last received steering command
    beacon: bool = False  # beacon status on/off
    dist_L: float = 0  # left distance sensor reading in cm
    dist_R: float = 0  # right distance sensor reading in cm
    _lock = threading.Lock()  # lock to ensure thread safety

class SharedState:
    """Singleton class to manage shared state with thread safety."""
    _instance = None

    def __new__(cls, x=240, y=30, theta=np.pi/2):
        """Creates a new instance of State if none exists, otherwise returns the existing one."""
        if cls._instance is None:
            cls._instance = State(x, y, theta)
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Resets the singleton instance."""
        cls._instance = None
    
    def __del__(cls):
        cls._instance = None
