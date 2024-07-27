import sys
import time
import math
import RPi.GPIO as GPIO
import serial
import spidev
from spidev import SpiDev

class Mq6Module:
    class MCP3008:
        def __init__(self, bus=0, device=0):
            self.bus, self.device = bus, device
            self.spi = SpiDev()
            self.open()
            self.spi.max_speed_hz = 1000000  # 1MHz

        def open(self):
            self.spi.open(self.bus, self.device)
            self.spi.max_speed_hz = 1000000  # 1MHz

        def read(self, channel=0):
            cmd1 = 4 | 2 | ((channel & 4) >> 2)
            cmd2 = (channel & 3) << 6

            adc = self.spi.xfer2([cmd1, cmd2, 0])
            data = ((adc[1] & 15) << 8) + adc[2]
            return data

        def close(self):
            self.spi.close()

    class MQ:
        MQ_PIN = 0  # define which analog input channel you are going to use (MCP3008)
        RL_VALUE = 5  # define the load resistance on the board, in kilo ohms
        RO_CLEAN_AIR_FACTOR = 9.83  # RO_CLEAR_AIR_FACTOR=(Sensor resistance in clean air)/RO,
        # which is derived from the chart in datasheet

        ######################### Software Related Macros #########################
        CALIBARAION_SAMPLE_TIMES = 50  # define how many samples you are going to take in the calibration phase
        CALIBRATION_SAMPLE_INTERVAL = 500  # define the time interval (in milliseconds) between each sample in the
        # calibration phase
        READ_SAMPLE_INTERVAL = 50  # define the time interval (in milliseconds) between each sample in
        READ_SAMPLE_TIMES = 5  # define how many samples you are going to take in normal operation
        # normal operation

        ######################### Application Related Macros ######################
        GAS_LPG = 0

        def __init__(self, Ro=10, analogPin=0):
            self.Ro = Ro
            self.MQ_PIN = analogPin
            self.adc = Mq6Module.MCP3008()

            self.LPGCurve = [2.3, 0.30, -0.42]  # two points are taken from the curve.
            # with these two points, a line is formed which is "approximately equivalent"
            # to the original curve.
            # data format:{ x, y, slope}; point1: (lg200, 0.21), point2: (lg10000, -0.59)

            print("Calibrating...")
            self.Ro = self.MQCalibration(self.MQ_PIN)
            print("Calibration is done...\n")
            print("Ro=%f kohm" % self.Ro)

        def MQPercentage(self):
            val = {}
            read = self.MQRead(self.MQ_PIN)
            if self.Ro != 0:  # Check if Ro is not zero to avoid division by zero
                val["GAS_LPG"] = self.MQGetGasPercentage(read / self.Ro, self.GAS_LPG)
            else:
                val["GAS_LPG"] = 0

            return val

        def MQResistanceCalculation(self, raw_adc):
            if raw_adc == 0:
                return 0.0  # Return 0 to avoid division by zero
            return float(self.RL_VALUE * (1023.0 - raw_adc) / float(raw_adc))

        def MQCalibration(self, mq_pin):
            val = 0.0
            for i in range(self.CALIBARAION_SAMPLE_TIMES):
                val += self.MQResistanceCalculation(self.adc.read(mq_pin))
                time.sleep(self.CALIBRATION_SAMPLE_INTERVAL / 1000.0)

            val = val / self.CALIBARAION_SAMPLE_TIMES

            val = val / self.RO_CLEAN_AIR_FACTOR

            return val

        def MQRead(self, mq_pin):
            rs = 0.0

            for i in range(self.READ_SAMPLE_TIMES):
                rs += self.MQResistanceCalculation(self.adc.read(mq_pin))
                time.sleep(self.READ_SAMPLE_INTERVAL / 1000.0)

            rs = rs / self.READ_SAMPLE_TIMES

            return rs

        def MQGetGasPercentage(self, rs_ro_ratio, gas_id):
            if gas_id == self.GAS_LPG:
                return self.MQGetPercentage(rs_ro_ratio, self.LPGCurve)
            return 0

        def MQGetPercentage(self, rs_ro_ratio, pcurve):
            if rs_ro_ratio <= 0:
                return 0.0
            else:
                return math.pow(10, (((math.log(rs_ro_ratio) - pcurve[1]) / pcurve[2]) + pcurve[0]))
    

    def __init__(self, id, pin):
        self.id = id
        self.mq6_device = pin
        self.mcp3008 = self.MCP3008()
        self.mq = self.MQ()

    def get_id(self):
        return self.id

# instances of Mq6Module
mq6_modules = [
    Mq6Module(id=1, pin=0),
]
