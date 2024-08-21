import serial

# Uncomment ↑ for real car / ↓ for simulator

# import sys
# import os

# current_dir = os.path.dirname(os.path.realpath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
# sys.path.append(parent_dir)
# import IP3.Simulator as serial

import time
import pyaudio
import numpy as np

class KITT:
    def __init__(self, port, baudrate=115200):
        self.serial = serial.Serial(port, baudrate, rtscts=True)
        print("Serial connection established.")

        self.code = 0x84B3E375 # 32-bit LFSR
        self.send_command(f'F10000\n')
        self.send_command(f'B2000\n')
        self.send_command(f'R2000\n')
        self.send_command(f'C{self.code}\n')

        self.distance_measurements = [] # Format [time, left_sensor, right_sensor]
        self.recordings = [] # Format [time, mic1, mic2, mic3, mic4, mic5]
        self.begin_time = time.time()

        self.device_index = 1 # Port to which the recording device is connected, tends to stay constant
        self.Fs = 48000 # Sampeling frequency of recording device

    def send_command(self, command):
        self.serial.write(command.encode())

    def set_speed(self, speed):
        self.send_command(f'M{speed}\n')

    def set_angle(self, angle):
        self.send_command(f'D{angle}\n')

    def stop(self):
        self.set_speed(150)
        self.set_angle(150)

    def onsound(self):
        self.send_command(f'A1\n')

    def offsound(self):
        self.send_command(f'A0\n')

    def distance_measurement(self):
        self.send_command('Sd\n') # Command car to take distance measurement
        received = self.serial.read_until(b'\x04') # Read distances form KITT
        received = received.decode()
        
        # Find the positions of "USL" and "USR" in the string
        usl_pos = received.find('USL')
        usr_pos = received.find('USR')

        usl = float(received[usl_pos+3:usr_pos])
        usr = float(received[usr_pos+3:-2])

        self.distance_measurements.append([time.time() - self.begin_time, usl, usr])

    def record(self, N):
        pyaudio_handle = pyaudio.PyAudio()

        # for i in range(pyaudio_handle.get_device_count()):
        #     device_info = pyaudio_handle.get_device_info_by_index(i)
        # print(i, device_info['name'])

        stream = pyaudio_handle.open(input_device_index=self.device_index,
                                     channels=5,
                                     format=pyaudio.paInt16,
                                     rate=self.Fs,
                                     input=True)

        samples = stream.read(N * self.Fs)

        data = np.frombuffer(samples, dtype='int16')
        self.recordings.append([time.time() - self.begin_time, data[::5], data[1::5], data[2::5], data[3::5], data[4::5]])
    
    def __del__(self):
        self.serial.close()


def wasd(kitt):
    print('wasd, e = beacon on, q = beacon off, r = distance measurement, t = terminate')
    while True:
        key = input()
        if key == 'w':
            kitt.set_speed(160)
        elif key == 's':
            kitt.set_speed(140)
        elif key == 'a':
            kitt.set_angle(100)
        elif key == 'd':
            kitt.set_angle(200)
        elif key == 'x':
            kitt.stop()
        elif key == 'e':
            kitt.onsound()
        elif key == 'q':
            kitt.offsound()
        elif key == 'r':
            kitt.distance_measurement()
            print(kitt.distance_measurements[-1])
        elif key == 't':
            kitt.stop()
            break

if __name__ == "__main__":
    kitt_instance = KITT('/dev/cu.RNBT-DA79')
    wasd(kitt_instance)