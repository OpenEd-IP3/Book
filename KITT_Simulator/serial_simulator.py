import time
import threading
from KITT_Simulator.dynamics_simulator import Dynamics
import numpy as np
import matplotlib.pyplot as plt
from KITT_Simulator.shared_state import SharedState
from KITT_Simulator.GUI_notebook import GUI
import logging

class Serial:
    """Class to simulate serial communication with the car."""
    def __init__(self, port, baudrate, rtscts=True, x=240, y=30, theta=np.pi/2):
        """Initializes the Serial class with port, baudrate, and initial state, and starts the dynamics thread."""
        # logging.basicConfig(level=logging.WARNING)
        #logging.basicConfig(filename='KITT_Simulator/logs/serialSimulator.log', level=logging.DEBUG)
        logging.info("Starting Serial Communication")

        self.port = port
        self.baudrate = baudrate
        self.rtscts = rtscts

        self.send_buffer = []  # Buffer for storing commands to be sent

        logging.info("Serial: Starting Dynamics")
        self.state = SharedState(x, y, theta)
        self.dynamics = Dynamics(self.state)

        # Initialize the GUI
        logging.info("Serial: Starting GUI")
        self.gui = GUI(self.state, self.state.motor_command, self.state.servo_command)
        self.gui.display()
        
       # self.update_queue = queue.Queue()
        
        logging.info("Serial: Starting Dynamics Thread")
        self.update_thread = threading.Thread(target=self.run_dynamics)
        self.update_thread.daemon = True
        self.stop_thread = threading.Event()
        self.update_thread.start()

    def write(self, command):
        """Writes a command to the serial port and updates the shared state accordingly."""
        with self.state._lock:
            logging.debug(f"Received command: {command}")

            if command[0] == ord('M'):
                motor_command = int(command[1:-1])
                self.state.motor_command = motor_command
            elif command[0] == ord('D'):
                servo_command = int(command[1:-1])
                self.state.servo_command = servo_command

    def read_until(self, end):
        """Reads from the send buffer until a specified end character is found."""
        return self.send_buffer.pop(0)  # Return the first element in the send buffer

    def run_dynamics(self):
        """Continuously updates the state using dynamics every 50ms."""
        update_freq = 2  # Desired updates per second
        update_interval = 1 / update_freq  # Time per update in seconds

        while not self.stop_thread.is_set():
            start_time = time.time()  # Start time of this loop

            logging.debug("Running dynamics update")
            self.dynamics.update_state()

            # Enqueue the updated state for processing in the main thread
            self.gui.update()
            
            logging.debug(f"X: {self.state.x}, Y: {self.state.y}, Theta: {self.state.theta}")

            elapsed_time = time.time() - start_time  # Time taken for this update loop
            sleep_time = update_interval - elapsed_time

            if sleep_time > 0:
                time.sleep(sleep_time)  # Sleep only if we have time remaining in the frame
            else:
                logging.warning("Dynamics thread running too slow.")
    
    def close(self):
        """Closes the serial connection."""
        logging.info("Closing Serial Communication")
        if self.update_thread.is_alive():
            self.stop_thread.set()
            self.update_thread.join()
        SharedState.reset()
        logging.info("Serial Communication closed.")

    def __del__(self):
        """Destructor to clean up when the Serial object is deleted."""
        self.close()
