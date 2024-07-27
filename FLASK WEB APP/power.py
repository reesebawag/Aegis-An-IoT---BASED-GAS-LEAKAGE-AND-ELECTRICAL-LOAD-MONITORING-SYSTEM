import serial
import time

class Power_data:
    def __init__(self, id, pin):
        self.id = id
        self.pin = pin
        self.serial = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        self.serial.flush()

    def get_electricalsensor_readings(self):
        if self.serial.in_waiting > 0:
            data = self.serial.readline().decode().rstrip()
            return data  # Modify this part to process the data as needed
        else:
            return None  # Adjust the sleep time as needed

powers = [
    Power_data(id=1, pin=0)
]