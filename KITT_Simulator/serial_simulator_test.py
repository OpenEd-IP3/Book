import time
import logging

try:
    from KITT_Simulator.serial_simulator import Serial # Simulator
except ImportError:
    from serial_simulator import Serial # Simulator
else:
    raise ImportError("Could not import the required modules.")

def test_serialSimulator():
    serial_obj = Serial('/dev/cu.RNBT-3F3B', 115200)
    time.sleep(5)

    # Stand Still
    serial_obj.write('M150\n'.encode())
    serial_obj.write('D150\n'.encode())
    time.sleep(2)

    # Move forward
    serial_obj.write('M165\n'.encode())
    time.sleep(1)

    # Turn Right
    serial_obj.write('D180\n'.encode())
    time.sleep(0.8)

    # Move forward
    serial_obj.write('D150\n'.encode())
    time.sleep(0.5)

    # Turn Left
    serial_obj.write('D120\n'.encode())
    time.sleep(0.5)

    # Stop
    serial_obj.write('D150\n'.encode())
    serial_obj.write('M150\n'.encode())
    time.sleep(4)

    # Drive Backwards
    serial_obj.write('M135\n'.encode())
    time.sleep(3.5)

    # Turn Right
    serial_obj.write('M160\n'.encode())
    serial_obj.write('D200\n'.encode())
    time.sleep(4)

    # Stop
    serial_obj.write('M150\n'.encode())
    serial_obj.write('D150\n'.encode())
    time.sleep(5)

    serial_obj.close()

if __name__ == "__main__":
    test_serialSimulator()