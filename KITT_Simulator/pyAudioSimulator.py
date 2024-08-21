import time as time
import numpy as np
import matplotlib.pyplot as plt
from sharedState import SharedState
import struct
from KITT_Control.Localization import Localization
import random
from scipy.fft import fft, ifft
from scipy.io import wavfile

class PyAudio:

    def __init__(self, x=240, y=30, theta=np.pi/2):
        self.state = SharedState(x , y, theta)
        self.state.beacon = True # Turn on the beacon for testing!!

    def get_device_count(self):
        return 5
    
    def get_device_info_by_index(self, index):
        example_output = [
            {'index': 0, 'structVersion': 2, 'name': 'iPhone Microphone', 'hostApi': 0, 'maxInputChannels': 1, 'maxOutputChannels': 0, 'defaultLowInputLatency': 0.12841666666666668, 'defaultLowOutputLatency': 0.01, 'defaultHighInputLatency': 0.13775, 'defaultHighOutputLatency': 0.1, 'defaultSampleRate': 48000.0},
            {'index': 1, 'structVersion': 2, 'name': 'AudioBox 1818 VSL', 'hostApi': 0, 'maxInputChannels': 18, 'maxOutputChannels': 18, 'defaultLowInputLatency': 0.01, 'defaultLowOutputLatency': 0.0045578231292517, 'defaultHighInputLatency': 0.1, 'defaultHighOutputLatency': 0.014716553287981859, 'defaultSampleRate': 44100.0},
            {'index': 2, 'structVersion': 2, 'name': 'MacBook Pro Microphone', 'hostApi': 0, 'maxInputChannels': 1, 'maxOutputChannels': 0, 'defaultLowInputLatency': 0.03285416666666666, 'defaultLowOutputLatency': 0.01, 'defaultHighInputLatency': 0.0421875, 'defaultHighOutputLatency': 0.1, 'defaultSampleRate': 48000.0},
            {'index': 3, 'structVersion': 2, 'name': 'MacBook Pro Speakers', 'hostApi': 0, 'maxInputChannels': 0, 'maxOutputChannels': 2, 'defaultLowInputLatency': 0.01, 'defaultLowOutputLatency': 0.018708333333333334, 'defaultHighInputLatency': 0.1, 'defaultHighOutputLatency': 0.028041666666666666, 'defaultSampleRate': 48000.0},
            {'index': 4, 'structVersion': 2, 'name': 'Microsoft Teams Audio', 'hostApi': 0, 'maxInputChannels': 2, 'maxOutputChannels': 2, 'defaultLowInputLatency': 0.01, 'defaultLowOutputLatency': 0.0013333333333333333, 'defaultHighInputLatency': 0.1, 'defaultHighOutputLatency': 0.010666666666666666, 'defaultSampleRate': 48000.0},
        ]
        return example_output[index]
    
    def open(self, input_device_index, channels, format, rate, input):
        self.stream = Stream(self.state)
        return self.stream

class Stream:

    def __init__(self, state):
        self.state = state

        # Dictionary containing 4 pulses (1 sec) for each 5 cm distance
        self.pulse_dict = {}
        with open("KITT_Simulator/pulses_recording.txt", "r") as f: # Recording at 44100Khz
            for line in f:
                line = line.split(sep=" ")
                self.pulse_dict[int(line[0][:-1])] = [int(i) for i in line[1:-1]]
        # self.__plot_2d_arrays([np.linspace(0, 1, len(self.pulse_dict[30])) ,self.pulse_dict[30]])

        # Array containing 1 sec of silence
        with open("KITT_Simulator/silence.txt", "r") as f:
            for line in f:
                line = line.split(sep=" ")
                self.silence = [int(i) for i in line[1:-1]]
        # self.__plot_2d_arrays([np.linspace(0, 1, len(self.silence)) ,self.silence])
        
    def read(self, length):
        """
        Returns an interleaved, encoded recording from the microphones
        """
        self.random_offset = random.randint(1000, 10000)

        if not self.state.beacon: # If the beacon is off, return silence
            return self.__interleave_and_prepare_buffer(self.silence, self.silence, self.silence, self.silence, self.silence)
        
        D1, D2, D3, D4, D5 = self.__dist() # Calculate the distance to each microphone
        # print(self.__dist())

        # Get a recording from each microphone for that distance
        R1 = self.__dist_to_audio(D1)
        R2 = self.__dist_to_audio(D2)
        R3 = self.__dist_to_audio(D3)
        R4 = self.__dist_to_audio(D4)
        R5 = self.__dist_to_audio(D5)

        # Interleave and put on buffer
        return self.__interleave_and_prepare_buffer(R1, R2, R3, R4, R5)

    def __dist(self):
        """
        Calculate the distance from the car to each microphone
        D1 = the distance from microphone 1 to the car
        """

        mic_coor = np.array([[0, 0], [0, 480], [480, 480], [480, 0], [0, 240]])
        car_coor = np.array([self.state.x, self.state.y])

        D1 = np.linalg.norm(mic_coor[0]-car_coor)
        D2 = np.linalg.norm(mic_coor[1]-car_coor)
        D3 = np.linalg.norm(mic_coor[2]-car_coor)
        D4 = np.linalg.norm(mic_coor[3]-car_coor)
        D5 = np.linalg.norm(mic_coor[4]-car_coor)

        return D1, D2, D3, D4, D5
    
    def __dist_to_audio(self, distance):
        """
        Takes a distance from the car to the microphones, returns the nearest recording
        """
        distance = self.__round5(distance)

        try:
            return self.pulse_dict[distance]
        except:
            print("ERROR: No recording available for this distance")
            return self.silence
        
    def ch3(self, x, y):
        Nx = len(x) # Length of x
        Ny = len(y) # Length of y
        L = Ny + Nx - 1 # Length of h
        self.epsi = 0.001
        if (Nx > Ny):
            y = np.concatenate((y, np.zeros(len(x) - len(y))))
        else:
            x = np.concatenate((x, np.zeros(len(y) - len(x))))

        # Deconvolution in frequency domain
        Y = fft(y)
        X = fft(x)
        H = Y / X

        # Threshold to avoid blow ups of noise during inversion
        ii = np.absolute(X) < self.epsi * max(np.absolute(X))
        for index, i in enumerate(ii):
            if i:
                H[index] = 0
            else:
                H[index] = H[index]

        h = np.real(ifft(H)) 
        # ensure the result is real-valued
        h = h[0:L]
        return h

    @staticmethod
    def __interleave_and_prepare_buffer(*arrays):
        """
        Interleaves elements from multiple arrays and prepares a buffer for Bluetooth transmission,
        encoding the data as 16-bit signed integers (PAINT16).

        Parameters:
            *arrays (list of lists): Variable number of input lists/arrays.

        Returns:
            bytearray: A bytearray buffer ready for Bluetooth transmission.
        """
        # Ensure all arrays have the same length
        length = len(arrays[0])
        for array in arrays:
            if len(array) != length:
                raise ValueError("All input arrays must have the same length")

        # Interleave the arrays
        interleaved_list = []
        for i in range(length):
            for array in arrays:
                interleaved_list.append(array[i])

        # Pack the interleaved list as 16-bit signed integers
        format_string = f'<{len(interleaved_list)}h'  # Little-endian (<) and 16-bit signed integer (h)
        packed_data = struct.pack(format_string, *interleaved_list)

        # Convert the packed data to a bytearray
        buffer = bytearray(packed_data)

        return buffer

    @staticmethod
    def __round5(x, base=5):
        return base * round(x/base)

    @staticmethod
    def __plot_2d_arrays(arrays):
        """
        Plots one or more 2D arrays.
        arrays = [[x-axis, y-axis], ...]
        """
        
        plt.plot(arrays[0], arrays[1], label="0")
        
        plt.legend()
        plt.xlabel('t (sec)')
        plt.ylabel('Y-axis')
        plt.title('Audio Plot')
        plt.show()

class paInt16:
    pass

if __name__ == "__main__":
    pyaudio_handle = PyAudio()

    for i in range(pyaudio_handle.get_device_count()):
        device_info = pyaudio_handle.get_device_info_by_index(i)
        print(i, device_info['name'])

    device_index = int(input('Enter device index: '))
    Fs = 44100

    stream = pyaudio_handle.open(input_device_index=device_index,
                                channels=5,
                                format=paInt16,
                                rate=Fs,
                                input=True)

    samples = stream.read(Fs*6)
    data = np.frombuffer(samples, dtype='int16')

    plt.plot(data[0::5])
    plt.plot(data[1::5])
    plt.plot(data[2::5])
    plt.plot(data[3::5])
    plt.plot(data[4::5])
    plt.show()

    recording = np.array([data[0::5], data[1::5], data[2::5], data[3::5], data[4::5]]).T

    localization = Localization(recording)

