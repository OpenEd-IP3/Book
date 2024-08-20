from scipy.io import wavfile
import logging
import scipy.signal as signal
from scipy.fft import fft, ifft

class Localization:
    def __init__(self, recording, debug=False):
        """
        Initializes the Localization class with the given recordings.
        
        Parameters:
        - recording: A 2D numpy array where each row is a recording from one microphone.
        - debug: Boolean to enable debug logging.
        """
        self.recording = recording
        self.num_pulses = 40
        self.debug = debug
        
        # Load the reference signal
        self.Fs, self.refSignal = wavfile.read("files/student_recording/reference.wav")  # Reference signal
        self.refSignal = self.refSignal[200000:230000, 0]  # Use only one channel
        self.refSignal = self.refSignal / np.max(np.abs(self.refSignal))  # Normalize the reference signal
        
        # Define the microphone positions in cm
        self.mic_positions = np.array([[0, 0], [460, 0], [460, 460], [0, 460], [230, 0]])
        
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        
        # Localize the sound source for each pulse
        self.localizations = self.localization()

    def localization(self):
        """
        Localize the sound source by processing the recordings.
        
        Returns:
        - x_car: Estimated x-coordinate of the sound source.
        - y_car: Estimated y-coordinate of the sound source.
        """
        pulse_length = len(self.recording[:, 0]) // self.num_pulses  # Calculate the length of each pulse segment
        print(f"--- Pulse Length: {pulse_length}, {len(self.recording[:, 0])} ---")

        tdoa_12 = []
        tdoa_13 = []
        tdoa_14 = []

        for i in range(self.num_pulses):
            start = i * pulse_length
            end = start + pulse_length
            
            # Extract the pulse from each recording
            pulse_rec = self.recording[start:end, :]

            # Calculate TDOA between different microphone pairs using the extracted pulse
            D12 = self.TDOA(pulse_rec[:, 0], pulse_rec[:, 1])
            D13 = self.TDOA(pulse_rec[:, 0], pulse_rec[:, 2])
            D14 = self.TDOA(pulse_rec[:, 0], pulse_rec[:, 3])

            tdoa_12.append(D12)
            tdoa_13.append(D13)
            tdoa_14.append(D14)

            if self.debug:
                logging.debug(f"Pulse {i + 1}: TDOA12={D12}, TDOA13={D13}, TDOA14={D14}")

        sorted_tdoa_12 = np.sort(tdoa_12)
        sorted_tdoa_13 = np.sort(tdoa_13)
        sorted_tdoa_14 = np.sort(tdoa_14)
        plt.plot(sorted_tdoa_12, label="TDOA12")
        plt.show()

        avg_D12 = np.mean(sorted_tdoa_12[10:-10]) * 34300
        avg_D13 = np.mean(sorted_tdoa_13[10:-10]) * 34300
        avg_D14 = np.mean(sorted_tdoa_14[10:-10]) * 34300

        if self.debug:
            logging.debug(f"Averaged TDOA12: {avg_D12}, TDOA13: {avg_D13}, TDOA14: {avg_D14}")

        # Calculate the 2D coordinates based on the averaged TDOA measurements
        x_car, y_car = self.coordinate_2d(avg_D12, avg_D13, avg_D14)
        
        logging.info(f"Final localized position: x={x_car}, y={y_car}")
        return x_car, y_car

    def TDOA(self, rec1, rec2):
        """
        Calculate the Time Difference of Arrival (TDOA) between two recordings.
        
        Parameters:
        - rec1: Extracted pulse recording from the first microphone.
        - rec2: Extracted pulse recording from the second microphone.
        
        Returns:
        - TDOA: The estimated time difference of arrival between the two recordings.
        """
        # Cross-correlate the reference signal with each extracted pulse
        corr1 = self.ch3(rec1, self.refSignal)
        corr2 = self.ch3(rec2, self.refSignal)
        
        # Find the lag with the maximum correlation value (which corresponds to the arrival time)
        lag1 = np.argmax(corr1) - (len(self.refSignal) - 1)
        lag2 = np.argmax(corr2) - (len(self.refSignal) - 1)
        
        # Calculate TDOA
        TDOA = (lag2 - lag1) / self.Fs  # Convert lag difference to time difference in seconds

        # plt.plot(corr1, alpha=0.5)
        # plt.plot(corr2, alpha=0.5)
        # plt.scatter(lag1 + len(self.refSignal) - 1, corr1[np.argmax(corr1)], color='red')
        # plt.scatter(lag2 + len(self.refSignal) - 1, corr2[np.argmax(corr2)], color='red')
        # plt.show()
        
        if self.debug:
            logging.debug(f"Lag1: {lag1}, Lag2: {lag2}, TDOA: {TDOA}")
        
        return TDOA
    
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

    def coordinate_2d(self, D12, D13, D14):
        # Calculate other microphone differences
        D23 = (D13 - D12)
        D24 = (D14 - D12)
        D34 = (D14 - D13)

        # Microphone coordinates
        xyMic = np.array([[0, 0], [0, 460], [460, 460], [460, 0]])

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
    # read wav file in folder files
    Fs, recording = wavfile.read("files/student_recording/record_x178_y439.wav")
    
    # Initialize the Localization object
    localization = Localization(recording, debug=True)
    
    # Get the localized position
    x_car, y_car = localization.localizations
    print(f"Estimated position: x={x_car}, y={y_car}")
