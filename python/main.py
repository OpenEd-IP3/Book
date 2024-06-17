import tkinter as tk
from objects.Arena import Arena
from objects.Car import Car
from objects.Communication import Micarray
from objects.Communication import Beacon


class Simulator:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=800, height=600, bg = 'white')
        self.canvas.pack()
        self.arena = Arena(self.canvas)
        self.car = Car(self.canvas)
        #self.microphone = Micarray(self.canvas)
        #self.beacon = Beacon(self.canvas)
        self.master.bind("<KeyPress>", self.on_keypress)
        self.arena.draw()
        self.car.draw_car()

        #self.microphone.draw_micarray()


    def on_keypress(self, event):
        if event.keysym == 'Up':
            self.car.move_forward(10)
        elif event.keysym == 'Down':
            self.car.move_backward(10)
        elif event.keysym == 'Left':
            self.car.update_orientation(-5)
        elif event.keysym == 'Right':
            self.car.update_orientation(5)
        else:
            return
        self.car.draw_car()

if __name__ == "__main__":
    x = [1, 2, 3]
    y = [1, 2, 3]
    angle = 45

    root = tk.Tk()
    sim = Simulator(root)
    root.mainloop()