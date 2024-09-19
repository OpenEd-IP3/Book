import time as time
import numpy as np
import matplotlib.pyplot as plt

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

        self.pulse = []
        self.silence = []
        # Load the recording
        self.load_recordings()

        self.Fs = 44100  # Sampling frequency
        self.num_pulses = 3
        self.speed_of_sound = 34300  # Speed of sound in cm/s

    def load_recordings(self):
        # Load the recordings from files
        try:
            with open("KITT_Simulator/simulator_data/pulses_recording.txt", "r") as f:
                line = f.readline()
                self.pulse = np.array([int(i) for i in line.strip().split()[1:]], dtype=np.int16)

            with open("KITT_Simulator/simulator_data/silence.txt", "r") as f:
                self.silence = np.array([int(i) for i in f.readline().strip().split()[1:]], dtype=np.int16)
        except:
            with open("simulator_data/pulses_recording.txt", "r") as f:
                line = f.readline()
                self.pulse = np.array([int(i) for i in line.strip().split()[1:]], dtype=np.int16)
            with open("simulator_data/silence.txt", "r") as f:
                self.silence = np.array([int(i) for i in f.readline().strip().split()[1:]], dtype=np.int16)

    def read(self, num_frames):
        distances = self.__dist()

        distances = [dist * self.Fs / self.speed_of_sound for dist in distances] # Convert distances to samples

        R1 = self.pulse[1000-int(distances[0]):]
        R2 = self.pulse[1000-int(distances[1]):]
        R3 = self.pulse[1000-int(distances[2]):]
        R4 = self.pulse[1000-int(distances[3]):]
        R5 = self.pulse[1000-int(distances[4]):]

        R1 = R1[:33000]
        R2 = R2[:33000]
        R3 = R3[:33000]
        R4 = R4[:33000]
        R5 = R5[:33000]

        buffer = self.__interleave_and_prepare_buffer(R1, R2, R3, R4, R5)
        return buffer

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

    @staticmethod
    def __interleave_and_prepare_buffer(*arrays):
        # Interleave arrays and prepare buffer
        length = min(len(arr) for arr in arrays)
        arrays = [arr[:length] for arr in arrays]

        interleaved_list = np.vstack(arrays).reshape((-1,), order='F')
        buffer = interleaved_list.astype('<i2').tobytes()
        return buffer

class paInt16:
    pass

if __name__ == "__main__":
    pyaudio_handle = PyAudio(x=400, y=140, theta=np.pi/2)

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

    recording = np.array([data[0::5], data[1::5], data[2::5], data[3::5], data[4::5]]).T

    plt.plot(recording)
    plt.title("Recording")
    plt.show()

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