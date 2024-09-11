import matplotlib.pyplot as plt
import numpy as np
import threading
import queue
import time

class GUI:
    def __init__(self):
        # Initialize the plot
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, 480)
        self.ax.set_ylim(0, 480)
        self.ax.set_aspect('equal', 'box')
        self.point, = self.ax.plot([], [], 'ro')  # Initialize a point on the plot

        # Use a queue to safely pass data to the main thread
        self.queue = queue.Queue()

        # Start a timer to periodically update the plot
        self.timer = self.fig.canvas.new_timer(interval=100)
        self.timer.add_callback(self.update_plot)
        self.timer.start()

        # Show the plot in the main thread
        plt.ion()  # Turn on interactive mode
        plt.show()

    def update_plot(self):
        # Check if there is new data in the queue
        try:
            x, y = self.queue.get_nowait()
            # Update the point position
            self.point.set_data([x], [y])
            # Redraw the updated plot
            self.fig.canvas.draw()
        except queue.Empty:
            pass

    def update(self, x, y):
        # Put new data into the queue from any thread
        self.queue.put((x, y))

# Background thread function to simulate dynamics
def run_dynamics(gui):
    while True:
        # Simulate some new x, y data
        x = np.random.uniform(0, 480)
        y = np.random.uniform(0, 480)
        print(f"Updating plot with x={x}, y={y}")
        gui.update(x, y)  # Safely update using the queue
        time.sleep(1)

# Main function
def main():
    gui = GUI()
    # Start a background thread to update the GUI
    thread = threading.Thread(target=run_dynamics, args=(gui,))
    thread.daemon = True
    thread.start()

    # Keep the main thread alive to handle GUI events
    plt.show()

if __name__ == "__main__":
    main()