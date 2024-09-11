import matplotlib.pyplot as plt
import numpy as np
import time

class GUI:
    def __init__(self):
        # Initialize the plot
        self.fig, self.ax = plt.subplots()
        
        # Set axis limits to 480x480 with equal lengths
        self.ax.set_xlim(0, 480)
        self.ax.set_ylim(0, 480)
        self.ax.set_aspect('equal', 'box')
        
        # Initialize a point object on the plot
        self.point, = self.ax.plot([], [], 'ro')  # 'ro' is for a red dot
        
        # Draw the initial plot
        plt.ion()  # Turn on interactive mode
        plt.show()

    def update(self, x, y):
        # Clear previous point and plot the new point
        self.point.set_data(x, y)
        
        # Redraw the updated plot
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

if __name__ == '__main__':
    gui = GUI()
    for i in range(100):
        gui.update(2*i, i)
        time.sleep(0.1)