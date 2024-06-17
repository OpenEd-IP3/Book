import numpy as np
from scipy.fft import fft, ifft
from scipy.io import wavfile
import time
import matplotlib.pyplot as plt
import scipy

class Localization:

    def __init__(self, recording, debug=False):

        self.debug = debug
        self.recording = recording

        self.Fs, self.refSignal = wavfile.read("Recordings/refSignal.wav") # reference signal
        self.refSignal = self.refSignal / max(self.refSignal) # normalize
        self.refSignal = self.refSignal[0:1500] # cut to one pulse (maybe 4000 is better)

        self.bitcode = 'F3824D4D'  # transmitted bits [-]
        self.F_carrier = 5000  # carrier frequency [Hz]
        self.F_bit = 2000  # bit frequency [Hz]
        self.C_repetition = 20  # repetition count [-]

        self.xyCar = [481, 481] # car location [m]

        self.localization()

    def localization(self):
        """
        Perform localization based on time difference of arrival (TDOA) measurements.

        This method calculates the TDOA between the recorded audio signals from different microphones
        and uses these measurements to estimate the coordinates of the source of the sound.

        Returns:
            None
        """

        D12 = self.TDOA(self.recording[:, 0], self.recording[:, 1])
        D13 = self.TDOA(self.recording[:, 0], self.recording[:, 3])
        D14 = self.TDOA(self.recording[:, 0], self.recording[:, 2])
        D15 = self.TDOA(self.recording[:, 0], self.recording[:, 4])

        if self.debug:
            print(f"D12: {D12}")
            print(f"D13: {D13}")
            print(f"D14: {D14}")
            print(f"D15: {D15}")

        self.xyCar = self.coordinate_2d(D12, D13, D14)
        print(f"Location of car: {self.xyCar}")

    def TDOA(self, rec1, rec2):

        rec1 = rec1/max(rec1)   # normalize
        rec2 = rec2/max(rec2)   # normalize

        if self.debug:
            plt.plot(range(len(rec1)), rec1)
            plt.plot(range(len(rec2)), rec2)
            plt.title("Recordings")
            plt.show()

        dists = np.zeros(self.C_repetition) # initialize array for distances
        slice_size = len(rec1) // self.C_repetition # calculate slice size
        for i in range(self.C_repetition):
            slice_x = rec1[i*slice_size: i*slice_size+slice_size] 
            slice_y = rec2[i*slice_size: i*slice_size+slice_size]
            x = self.ch2(self.refSignal, slice_x)
            x = x / max(x)
            y = self.ch2(self.refSignal, slice_y)
            y = y / max(y)
            x_index, y_index = self.tdoa(x, y)
            dists[i] = (y_index - x_index) / self.Fs * 343

            if i < 3 and self.debug:
                plt.plot(range(len(x)), x, alpha=0.3)
                plt.plot(range(len(y)), y, alpha=0.3)
                plt.title(f"Channel estimate {(y_index - x_index) / self.Fs * 343}")
                plt.scatter(x_index, x[x_index], c='blue', marker='o', alpha=0.5)
                plt.scatter(y_index, y[y_index], c='red', marker='o', alpha=0.5)
                plt.show()
                print((y_index - x_index) / self.Fs * 343)

        dists = self.average_of_3_median_values(dists)
        return np.mean(dists)

    def tdoa(self, x, y):

        x_index = np.argmax(x)
        y_index = np.argmax(y)

        return x_index, y_index

    @staticmethod
    def ch2(x, y):
        """
        Channel estimation using matched filtering.
        """
        xr = x[::-1]
        h = np.convolve(y, xr, mode='full')  # filter xr with y
        alpha = np.dot(x.T, x)
        hhat = h / alpha
        return abs(hhat)

    def average_of_3_median_values(self, arr):
        sorted_arr = np.sort(arr)
        n = len(sorted_arr)

        if n % 2 == 0:
            # Even number of elements
            mid1 = n // 2 - 1
            mid2 = n // 2
            mid3 = n // 2 + 1
            three_medians = [sorted_arr[mid1], sorted_arr[mid2], sorted_arr[mid3]]
        else:
            # Odd number of elements
            mid = n // 2
            mid1 = mid - 1
            mid2 = mid
            mid3 = mid + 1
            three_medians = [sorted_arr[mid1], sorted_arr[mid2], sorted_arr[mid3]]

        average = np.mean(three_medians)
        return average

    def coordinate_2d(self, D12, D13, D14):
        # Calculate other microphone differences
        D23 = (D13 - D12)
        D24 = (D14 - D12)
        D34 = (D14 - D13)

        # Microphone coordinates
        xyMic = np.array([[0, 0], [4.80, 0], [0, 4.80], [4.80, 4.80]])

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
    start_t = time.perf_counter()

    # Read the .wav file
    Fs, recording = wavfile.read("Recordings/recording349152.wav")

    # Localize the sound source
    loc = Localization(recording, True)

    stop_t = time.perf_counter()
    print(f"Total time: {stop_t - start_t:0.4f}")
    print(f"Location of car: {loc.xyCar}")