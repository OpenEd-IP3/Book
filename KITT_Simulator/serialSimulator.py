import time as time
import dynamicsSimulator
# import gui

class Serial:
    def __init__(self, port, baudrate, rtscts, state = dynamicsSimulator.State(0, 0, 0, 0)):
        self.port = port
        self.baudrate = baudrate
        self.rtscts = rtscts

        self.motor_command = "150"
        self.servo_command = "150"

        self.send_buffer = [] # Buffer for storing commands to be sent

        self.state = state
        self.dynamics = dynamicsSimulator.Dynamics(self.state)
        # self.gui = gui.GUI()

    def write(self, command):
        command = command.decode()

        if command[0] == 'M':
            self.motor_command = command[1:]
        elif command[0] == 'D':
            self.servo_command = command[1:]
        
        self.dynamics.update_state(self.motor_command, self.servo_command)
        # self.gui.update(self.dynamics.state)

    def read_until(self, end):
        return self.send_buffer.pop(0) # Return the first element in the send buffer
    
    def close(self):
        self.__del__()
        
    def __del__(self):
        print('Serial port closed')
    
