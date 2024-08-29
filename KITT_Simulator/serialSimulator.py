import time
import threading
from KITT_Simulator.dynamicsSimulator import Dynamics
import numpy as np
import matplotlib.pyplot as plt
from KITT_Simulator.sharedState import SharedState
# from KITT_Simulator.GUI_notebook import GUI
from KITT_Simulator.serialGUI import GUI
import logging

class Serial:
    """Class to simulate serial communication with the car."""
    def __init__(self, port, baudrate, rtscts=True, x=240, y=30, theta=np.pi/2):
        """Initializes the Serial class with port, baudrate, and initial state, and starts the dynamics thread."""
        print("Serial connection established.")
        self.port = port
        self.baudrate = baudrate
        self.rtscts = rtscts

        self.send_buffer = []  # Buffer for storing commands to be sent

        self.state = SharedState(x, y, theta)
        self.dynamics = Dynamics(self.state)

        # Initialize the GUI
        self.gui = GUI(self.state)
        # self.gui.display() # Necessary for the GUI_notebook.py
        
        # Start the dynamics thread
        self.update_thread = threading.Thread(target=self.run_dynamics)
        self.update_thread.daemon = True
        self.stop_thread = threading.Event()
        self.update_thread.start()

    def write(self, command):
        """Writes a command to the serial port and updates the shared state accordingly."""
        with self.state._lock:
            command = command.decode()

            if command[0] == 'M':
                motor_command = int(command[1:-1])
                self.state.motor_command = motor_command
            elif command[0] == 'D':
                servo_command = int(command[1:-1])
                self.state.servo_command = servo_command

    def read_until(self, end):
        """Reads from the send buffer until a specified end character is found."""
        return self.send_buffer.pop(0)  # Return the first element in the send buffer

    def run_dynamics(self):
        """Continuously updates the state using dynamics every 50ms."""
        update_freq = 10
        while not self.stop_thread.is_set():
            start_time = time.time()
            
            self.dynamics.update_state()
            self.gui.update()
            
            delta_time = (time.time() - start_time) / 1000 - 1 / update_freq
            if delta_time > 0:
                time.sleep(delta_time)
            else:
                print(f"Warning: Dynamics update took {(time.time()-start_time)/1000} ms.")
    
    def close(self):
        """Closes the serial connection."""
        if self.update_thread.is_alive():
            self.stop_thread.set()
            self.update_thread.join()
        SharedState.reset()
        print("Serial connection closed.")

    def __del__(self):
        """Destructor to clean up when the Serial object is deleted."""
        self.close()
