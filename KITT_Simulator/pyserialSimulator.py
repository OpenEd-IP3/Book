import time as time
import numpy as np
import matplotlib.pyplot as plt
from serialSimulator import SharedState
import struct

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

        print("Distances: ")
        print(D1, D2, D3, D4, D5)
        print("Difference: ")
        print(D2-D1, D3-D1, D4-D1, D5-D1)

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

class Localization:

    def __init__(self, recording):

        self.recording = np.array(recording)

        self.Fs = 44100

        self.refSignal = self.load_reference()

        self.xyCar = [481, 481] # car location [cm]

        self.localize(self.recording)

    def load_reference(self):
        refSignal =  [] # reference signal
        with open("KITT_Simulator/pulses_recording.txt", "r") as f: # Recording at 44100Khz
            line = f.readline()
            line = line.split(sep=" ")
            refSignal = [int(i) for i in line[1:-1]]
            refSignal = np.array(refSignal[16000:21000])

        refSignal = refSignal / max(refSignal) # normalize

        # print(f"Refsignal shape: {refSignal.shape}")
        # plt.plot(refSignal)
        # plt.title("Reference recording")
        # plt.show()

        return refSignal

    def localize(self, recording):
        D12 = self.calculate_distance(recording[0], recording[1])
        D13 = self.calculate_distance(recording[0], recording[2])
        D14 = self.calculate_distance(recording[0], recording[3])

        print(f"Distances: {D12}, {D13}, {D14}")

        D12 = 73.71457719639113
        D13 = 248.4101510982589
        D14 = 205.8114133216988

        xyCar = self.coordinate_2d(D12, D13, D14)

        print(f"Car location: {xyCar}")

    def calculate_distance(self, recording0, recording1):
        plt.plot(recording0)
        plt.plot(recording1)
        plt.title("Recordings")
        plt.show()

        # Cross-correlation
        xcorr1 = np.abs(np.correlate(recording0, self.refSignal, mode='full'))
        xcorr1 = xcorr1 / max(xcorr1)

        xcorr2 = np.abs(np.correlate(recording1, self.refSignal, mode='full'))
        xcorr2 = xcorr2 / max(xcorr2)

        peaks1 = self.find_peaks(xcorr1)
        peaks2 = self.find_peaks(xcorr2)

        # Calculate distance
        print(f"Peaks: {peaks1}, {peaks2}")
        print(f"Peaks diff: {peaks2 - peaks1}")
        D = (np.mean(peaks2 - peaks1)) / self.Fs * 34300
        # D = 0

        plt.plot(xcorr1)
        plt.plot(xcorr2)
        plt.plot(peaks1, xcorr1[peaks1], 'ro')
        plt.plot(peaks2, xcorr2[peaks2], 'ro')
        plt.title(f"Cross-correlation: {D}")
        plt.show()

        return D
    
    def find_peaks(self, xcorr):
        results = []
        counter = 0
        for index, item in enumerate(xcorr):
            if counter > 0:
                counter -= 1
                continue
            if item > 0.8:
                results.append(index)
                counter = 300

        return np.array(results)
                

    def coordinate_2d(self, D12, D13, D14):
        # Calculate other microphone differences
        D23 = (D13 - D12)
        D24 = (D14 - D12)
        D34 = (D14 - D13)

        # Microphone coordinates
        xyMic = np.array([[0, 0], [0, 480], [480, 480], [480, 0]])

        A = np.array([[2 * (xyMic[1, 0] - xyMic[0, 0]), 2 * (xyMic[1, 1] - xyMic[0, 1]), -2 * D12, 0, 0],
                      [2 * (xyMic[2, 0] - xyMic[0, 0]), 2 * (xyMic[2, 1] - xyMic[0, 1]), 0, -2 * D13, 0],
                      [2 * (xyMic[3, 0] - xyMic[0, 0]), 2 * (xyMic[3, 1] - xyMic[0, 1]), 0, 0, -2 * D14],
                      [2 * (xyMic[2, 0] - xyMic[1, 0]), 2 * (xyMic[2, 1] - xyMic[1, 1]), 0, -2 * D23, 0],
                      [2 * (xyMic[3, 0] - xyMic[1, 0]), 2 * (xyMic[3, 1] - xyMic[1, 1]), 0, 0, -2 * D24],
                      [2 * (xyMic[3, 0] - xyMic[2, 0]), 2 * (xyMic[3, 1] - xyMic[2, 1]), 0, 0, -2 * D34]
                      ])

        b = np.array([(pow(D12, 2) - pow(np.linalg.norm(xyMic[0, :]), 2) + pow(np.linalg.norm(xyMic[1, :]), 2)),
                      (pow(D13, 2) - pow(np.linalg.norm(xyMic[0, :]), 2) + pow(np.linalg.norm(xyMic[2, :]), 2)),
                      (pow(D14, 2) - pow(np.linalg.norm(xyMic[0, :]), 2) + pow(np.linalg.norm(xyMic[3, :]), 2)),
                      (pow(D23, 2) - pow(np.linalg.norm(xyMic[1, :]), 2) + pow(np.linalg.norm(xyMic[2, :]), 2)),
                      (pow(D24, 2) - pow(np.linalg.norm(xyMic[1, :]), 2) + pow(np.linalg.norm(xyMic[3, :]), 2)),
                      (pow(D34, 2) - pow(np.linalg.norm(xyMic[2, :]), 2) + pow(np.linalg.norm(xyMic[3, :]), 2))
                      ])

        y = np.linalg.inv(A.T @ A) @ A.T @ b
        return y[0:2]

if __name__ == "__main__":

    ### PyAudio Test ###

    # Make a recording according to manual
    pyaudio_handle = PyAudio(100, 200)

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

    samples = stream.read(Fs*1)
    data = np.frombuffer(samples, dtype='int16')

    ### Localize recording as verification ###
    # Display received data
    print(data.shape)
    plt.plot(data[0::5])
    plt.plot(data[1::5])
    plt.plot(data[2::5])
    plt.plot(data[3::5])
    plt.plot(data[4::5])
    plt.title("Received Audio data")
    plt.show()

    loc = Localization([data[3000::5], data[3001::5], data[3002::5], data[3003::5], data[3004::5]])

    # # Test Localization Using Premade Recording
    # refRecording =  [] # reference signal
    # with open("field_recording_200_200.txt", "r") as f: # Recording at 44100Khz
    #     line = f.readline()
    #     line = line.split(sep=" ")
    #     refRecording = np.array([int(i) for i in line[0:-1]])

    # data = refRecording

    # # Display received data
    # print(data.shape)
    # plt.plot(data[0::5])
    # plt.plot(data[1::5])
    # plt.plot(data[2::5])
    # plt.plot(data[3::5])
    # plt.plot(data[4::5])
    # plt.title("Received Audio data")
    # plt.legend(["Mic 1", "Mic 2", "Mic 3", "Mic 4", "Mic 5"])
    # plt.show()

    # loc = Localization([data[0::5], data[1::5], data[2::5], data[3::5], data[4::5]])

