import time

class Timer:
    def __init__(self):
        self.start_time = 0
        self.end_time = 0

    def start(self):
        self.start_time = time.time()

    def end(self):
        self.end_time = time.time()

    def get_time(self):
        return self.end_time - self.start_time
    
    def reset(self):
        self.start_time = 0
        self.end_time = 0

# This should calculate time it takes for car to travel a distance until position is reached