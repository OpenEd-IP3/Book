# Comment / Uncoment for simulator
from KITT_Simulator.serial_simulator import Serial # Simulator
# from serial import Serial # Real Car
import time
import logging

def test_serialSimulator():
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(filename='serialSimulatorTest.log', level=logging.DEBUG, filemode='w')

    # time_var = 0.1
    logging.info("Starting Serial Communication")
    serial_obj = Serial('/dev/cu.RNBT-3F3B', 115200)
    time.sleep(5)

    # Stand Still
    logging.info("Stand Still")
    serial_obj.write('M150\n'.encode())
    serial_obj.write('D150\n'.encode())
    time.sleep(2)

    # Move forward
    logging.info("Move forward")
    serial_obj.write('M165\n'.encode())
    time.sleep(1)

    # Turn Right
    logging.info("Turn Right")
    serial_obj.write('D180\n'.encode())
    time.sleep(0.8)

    # Move forward
    logging.info("Move forward")
    serial_obj.write('D150\n'.encode())
    time.sleep(0.5)

    # Turn Left
    logging.info("Turn Left")
    serial_obj.write('D120\n'.encode())
    time.sleep(0.5)

    # Stop
    logging.info("Stop")
    serial_obj.write('D150\n'.encode())
    serial_obj.write('M150\n'.encode())
    time.sleep(4)

    # Drive Backwards
    logging.info("Drive Backwards")
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