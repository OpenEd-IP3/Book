import time as time
import numpy as np
import matplotlib.pyplot as plt
import struct
import random
from scipy.fft import fft, ifft
from scipy.io import wavfile

try: 
    from KITT_Simulator.shared_state import SharedState
except:
    from shared_state import SharedState

try: 
    from KITT_Simulator.KITT_Control.Localization import Localization
except:
    from KITT_Control.Localization import Localization

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

        # Dictionary containing pulses for each 5 cm distance
        self.pulse_dict = {}
        # Load the recordings
        self.load_recordings()
        # Align the pulses in the recordings
        self.align_recordings()

        self.Fs = 44100  # Sampling frequency
        self.num_pulses = 3
        self.speed_of_sound = 34300  # Speed of sound in cm/s

    def load_recordings(self):
        # Load the recordings from files
        try:
            with open("KITT_Simulator/simulator_data/pulses_recording.txt", "r") as f:
                for line in f:
                    line = line.strip().split()
                    key = int(line[0][:-1])
                    values = np.array([int(i) for i in line[1:]], dtype=np.int16)
                    self.pulse_dict[key] = values[3000:35000]
            with open("KITT_Simulator/simulator_data/silence.txt", "r") as f:
                self.silence = np.array([int(i) for i in f.readline().strip().split()[1:]], dtype=np.int16)
        except:
            with open("simulator_data/pulses_recording.txt", "r") as f:
                for line in f:
                    line = line.strip().split()
                    key = int(line[0][:-1])
                    values = np.array([int(i) for i in line[1:]], dtype=np.int16)
                    self.pulse_dict[key] = values[3000:35000]
            with open("simulator_data/silence.txt", "r") as f:
                self.silence = np.array([int(i) for i in f.readline().strip().split()[1:]], dtype=np.int16)

    def align_recordings(self):
        # Use cross-correlation to align the pulses
        self.aligned_pulse_dict = {}
        # Choose the reference recording at the closest distance (e.g., 30 cm)
        reference_distance = min(self.pulse_dict.keys())
        ref_recording = self.pulse_dict[reference_distance]
        # Extract the reference pulse
        ref_pulse = self.extract_pulse(ref_recording)
        for distance, recording in self.pulse_dict.items():
            # Find lag using cross-correlation
            lag = self.find_lag_using_cross_correlation(recording[:len(recording)//3], ref_pulse)
            # Shift the recording to align the pulses
            if lag >= 0:
                aligned_recording = recording[lag:]
            else:
                padding = np.zeros(-lag, dtype=recording.dtype)
                aligned_recording = np.concatenate((padding, recording))
            self.aligned_pulse_dict[distance] = aligned_recording

    def extract_pulse(self, recording):
        # Extract a pulse from the recording
        # Adjust indices based on where the pulse is expected
        # Here, we assume the pulse is between indices 16000 and 19500
        pulse_start = 1000
        pulse_end = 10000
        plt.plot(recording)
        plt.vlines([pulse_start, pulse_end], min(recording), max(recording), colors='r', linestyles='dashed')
        plt.show()
        return recording[pulse_start:pulse_end]

    def find_lag_using_cross_correlation(self, recording, ref_pulse):
        # Compute cross-correlation
        corr = np.correlate(recording, ref_pulse, mode='full')
        lag = np.argmax(corr) - len(ref_pulse) + 1
        return lag

    def read(self, length):
        if not self.state.beacon:
            return self.__interleave_and_prepare_buffer(
                self.silence, self.silence, self.silence, self.silence, self.silence
            )

        D1, D2, D3, D4, D5 = self.__dist()  # Calculate distances
        Fs = self.Fs

        # Calculate time delays in samples
        N1 = int((D1 / self.speed_of_sound) * Fs)
        N2 = int((D2 / self.speed_of_sound) * Fs)
        N3 = int((D3 / self.speed_of_sound) * Fs)
        N4 = int((D4 / self.speed_of_sound) * Fs)
        N5 = int((D5 / self.speed_of_sound) * Fs)

        # Get aligned recordings
        R1 = self.__dist_to_audio(D1)
        R2 = self.__dist_to_audio(D2)
        R3 = self.__dist_to_audio(D3)
        R4 = self.__dist_to_audio(D4)
        R5 = self.__dist_to_audio(D5)

        # Shift recordings according to time delays
        R1_shifted = self.shift_recording(R1, N1)
        R2_shifted = self.shift_recording(R2, N2)
        R3_shifted = self.shift_recording(R3, N3)
        R4_shifted = self.shift_recording(R4, N4)
        R5_shifted = self.shift_recording(R5, N5)

        # Ensure all recordings have the same length
        min_length = min(len(R1_shifted), len(R2_shifted), len(R3_shifted), len(R4_shifted), len(R5_shifted))
        R1_shifted = R1_shifted[:min_length]
        R2_shifted = R2_shifted[:min_length]
        R3_shifted = R3_shifted[:min_length]
        R4_shifted = R4_shifted[:min_length]
        R5_shifted = R5_shifted[:min_length]

        # Interleave and prepare buffer
        return self.__interleave_and_prepare_buffer(
            R1_shifted, R2_shifted, R3_shifted, R4_shifted, R5_shifted
        )

    def shift_recording(self, recording, delay_samples):
        # Shift the recording by padding zeros at the beginning
        if delay_samples > 0:
            padding = np.zeros(delay_samples, dtype=np.int16)
            shifted_recording = np.concatenate((padding, recording))
        else:
            shifted_recording = recording
        return shifted_recording

    def __dist(self):
        # Calculate distances from the car to each microphone
        mic_coor = np.array([[0, 0], [0, 460], [460, 460], [460, 0], [230, 0]])
        car_coor = np.array([self.state.x, self.state.y])

        D1 = np.linalg.norm(mic_coor[0] - car_coor)
        D2 = np.linalg.norm(mic_coor[1] - car_coor)
        D3 = np.linalg.norm(mic_coor[2] - car_coor)
        D4 = np.linalg.norm(mic_coor[3] - car_coor)
        D5 = np.linalg.norm(mic_coor[4] - car_coor)

        print(
            f"Distance differences: D12={D2-D1}, D13={D3-D1}, D14={D4-D1}, D15={D5-D1}"
        )
        return D1, D2, D3, D4, D5

    def __dist_to_audio(self, distance):
        # Get the aligned recording for the given distance
        distance = self.__round5(distance)
        try:
            recording = self.aligned_pulse_dict[distance]
        except KeyError:
            print(
                f"Warning: No recording available for {distance} cm, using default recording instead."
            )
            recording = self.aligned_pulse_dict[165]  # Default distance
        return recording

    @staticmethod
    def __interleave_and_prepare_buffer(*arrays):
        # Interleave arrays and prepare buffer
        length = min(len(arr) for arr in arrays)
        arrays = [arr[:length] for arr in arrays]

        interleaved_list = np.vstack(arrays).reshape((-1,), order='F')
        buffer = interleaved_list.astype('<i2').tobytes()
        return buffer

    @staticmethod
    def __round5(x, base=5):
        return base * round(x / base)

class paInt16:
    pass

if __name__ == "__main__":
    pyaudio_handle = PyAudio(x=40, y=140, theta=np.pi/2)

    for i in range(pyaudio_handle.get_device_count()):
        device_info = pyaudio_handle.get_device_info_by_index(i)
        print(i, device_info['name'])

    device_index = int(input('Enter device index: '))
    Fs = 44100

    stream = pyaudio_handle.open(
        input_device_index=device_index, channels=5, format=paInt16, rate=Fs, input=True
    )

    samples = stream.read(Fs * 6)
    data = np.frombuffer(samples, dtype='int16')

    recording = np.array(
        [data[0::5], data[1::5], data[2::5], data[3::5], data[4::5]]
    ).T

    # Proceed with localization using the corrected recordings
    pulse_dict = {}
    with open("KITT_Simulator/simulator_data/pulses_recording.txt", "r") as f:
        for line in f:
            line = line.strip().split()
            pulse_dict[int(line[0][:-1])] = [int(i) for i in line[1:]]

    refSignal = pulse_dict[30][16000:19500]

    localization = Localization(recording, refSignal, 3, Fs)

    # Get the localized position
    x_car, y_car = localization.localizations
    print(f"Estimated position: x={x_car}, y={y_car}")