import time
import threading
import numpy as np
import matplotlib.pyplot as plt
import logging
import queue  # Import queue to handle inter-thread communication


from KITT_Simulator.shared_state import SharedState
from KITT_Simulator.GUI_notebook import GUI
from KITT_Simulator.dynamics_simulator import Dynamics

# try:
#     from KITT_Simulator.shared_state import SharedState
#     from KITT_Simulator.gui import GUI
#     from KITT_Simulator.dynamics_simulator import Dynamics
# except ImportError:
#     from shared_state import SharedState
#     from GUI_notebook import GUI
#     from dynamics_simulator import Dynamics
# else:
#     raise ImportError("Could not import the required modules.")

class Serial:
    """Class to simulate serial communication with the car."""
    def __init__(self, port, baudrate, rtscts=True, x=240, y=30, theta=np.pi/2):
        """Initializes the Serial class with port, baudrate, and initial state, and starts the dynamics thread."""
        
        self.port = port
        self.baudrate = baudrate
        self.rtscts = rtscts

        self.send_buffer = []  # Buffer for storing commands to be sent

        self.state = SharedState(x, y, theta)
        self.dynamics = Dynamics(self.state)

        self.gui = GUI(self.state, self.state.motor_command, self.state.servo_command)  # Initialize the GUI
        self.gui.display()

        self.update_thread = threading.Thread(target=self.run_dynamics)
        self.update_thread.daemon = True
        self.stop_thread = threading.Event()
        self.update_thread.start()

    def write(self, command):
        """Writes a command to the serial port and updates the shared state accordingly."""
        with self.state._lock:
            if command[0] == ord('M'):
                motor_command = int(command[1:-1])
                self.state.motor_command = motor_command
            elif command[0] == ord('D'):
                servo_command = int(command[1:-1])
                self.state.servo_command = servo_command
            elif command[0] == ord('A'):
                if int(command[1:-1]) == 1:
                    self.state.beacon = True
                elif int(command[1:-1]) == 0:
                    self.state.beacon = False
                

    def read_until(self, end):
        """Reads from the send buffer until a specified end character is found."""
        return self.send_buffer.pop(0)  # Return the first element in the send buffer

    def run_dynamics(self):
        """Continuously updates the state using dynamics every 50ms."""
        update_freq = 2  # Desired updates per second
        update_interval = 1 / update_freq  # Time per update in seconds

        while not self.stop_thread.is_set():
            start_time = time.time()  # Start time of this loop

            self.dynamics.update_state()

            self.gui.update()

            elapsed_time = time.time() - start_time  # Time taken for this update loop
            sleep_time = update_interval - elapsed_time

            if sleep_time > 0:
                time.sleep(sleep_time)  # Sleep only if we have time remaining in the frame
            else:
                print("WARNING: Dynamics thread running too slow.")
    
    def close(self):
        """Closes the serial connection."""
        if self.update_thread.is_alive():
            self.stop_thread.set()
            self.update_thread.join()
        SharedState.reset()

    def __del__(self):
        """Destructor to clean up when the Serial object is deleted."""
        self.close()