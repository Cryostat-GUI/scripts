

import smbus
import time

# Import the MCP4725 module.
import Adafruit_MCP4725
from threading import Lock
from threading import Event
import pickle

import re
# import numpy as np

from zmqConnection import zmqServer
from zmqConnection import Timerthread


class I2CAdapter(object):
    """docstring for I2CObject"""

    def __init__(self, address=None, lock=None, *args, **kwargs):
        # super(I2CAdapter, self).__init__(*args, **kwargs)
        self.address = address
        if lock is None:
            self.comLock = Lock()
        else:
            self.comLock = lock


class DAC10V(I2CAdapter):
    """docstring for DAC10V"""

    # Note you can change the I2C address from its default (0x62), and/or the I2C
    # bus by passing in these optional parameters:
    # dac = Adafruit_MCP4725.MCP4725(address=0x49, busnum=1)

    # MCP4725 DAC.

    def __init__(self, correction_f=None, maxvolt=5, correction_n=0, address=0x61, *args, **kwargs):
        super(DAC10V, self).__init__(address=address, *args, **kwargs)
        self.dac = Adafruit_MCP4725.MCP4725(address=self.address, **kwargs)
        self.maxvolt = 10
        self._voltcap = maxvolt
        self.correction_n = correction_n
        if correction_f is None:
            with open('/home/pi/pressurecell/calibration/cal_DAC.pkl', 'rb') as f:
                self.correction_f = pickle.load(f)
        else:
            self.correction_f = correction_f

        self._voltage = 10
        self._n = 4096
        self.voltage = 0
        print('DAC10V initiated')

    def ncalc(self, volt):
        try:
            volt = self.correction_f(volt)
        except TypeError:
            volt += self.correction_n
        self._n = int(volt * 4096 / self.maxvolt)

        return self._n

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, volt):
        if volt > self._voltcap:
            volt = self._voltcap
        elif volt < 0:
            volt = 0        
        self._voltage = volt
        with self.comLock:
            self.dac.set_voltage(self.ncalc(volt))


class ADC5V(I2CAdapter):
    """docstring for ADC5V - ADS1115"""

    # Select configuration register, 0x01(01), address = 0x48
    # 0x8483(33923)   AINP = AIN0 and AINN = AIN1, +/- 2.048V
    # Continuous conversion mode, 128SPS

    # change PGA to +- 6.1V (never put more than 5V to it!), AIN0, AIN1, cont conv, 128SPS:
    # 0x8283 (33411)

    def __init__(self, calibration_f=None, address=0x48, *args, **kwargs):
        super(ADC5V, self).__init__(address=address, *args, **kwargs)
        self.bus = smbus.SMBus(1)
        with self.comLock:
            self.bus.write_i2c_block_data(0x48, 0x01, [0x80, 0x83])
        time.sleep(0.1)
        if calibration_f is None:
            with open('/home/pi/pressurecell/calibration/cal_ADC.pkl', 'rb') as f:
                self.calibration_f = pickle.load(f)
        else:
            self.calibration_f = calibration_f
        print('ADC5V initiated')

    def read_raw(self):
        with self.comLock:
            # Read data back from 0x00(00), 2 bytes
            data = self.bus.read_i2c_block_data(0x48, 0x00, 2)

        # Convert the data
        # raw_adc MSB, raw_adc LSB
        raw_adc = data[0] * 256 + data[1]

        if raw_adc > 32767:
            raw_adc -= 65535
        return raw_adc

    def read(self):
        raw = self.read_raw()
        data = self.calibration_f(raw)
        return data

    @property
    def voltage(self):
        self._voltage = float(self.read())
        return self._voltage


class PressureHandler(zmqServer, Timerthread):
    """docstring for PressureHandler"""

    def __init__(self, *args, **kwargs):
        super(PressureHandler, self).__init__(*args, **kwargs)
        self._pressure = 0
        self._dac = DAC10V()
        self._adc = ADC5V()
        self.data = dict()
        self.pressuremessage = re.compile(r'p *([0-9]+.*[0-9]*)')

    def handlefun(self, message_bytes):
        if message_bytes == b'p?':
            self.tcp_rep.send_string(f'{self._pressure}')
        elif message_bytes == b'data?':
            self.tcp_rep.send_json(self.data)
        else:
            message = message_bytes.decode()
            print('messages:', message_bytes, message)
            pressure = re.findall(self.pressuremessage, message)
            print('found pressure:', pressure)
            try:
                self._dac.voltage = float(pressure[0])
                self.tcp_rep.send_string(f'received: {message_bytes},this is {len(pressure)} numbers, successfully changed dac voltage! ')
            except IndexError:
                pass

                self.tcp_rep.send_string(f'received: {message_bytes}, can reply to "data?" with dictionary of data')

    def work(self):
        self.data['adc1'] = self._adc.voltage
        self.zmqquery_handle()


if __name__ == '__main__':
    stopevent = Event()
    dev = PressureHandler(event=stopevent, interval=0.005)
    dev.start()


    # try:
    #     time.sleep(200)
    # finally:
    #     stopevent.set()

    dac = DAC10V()
    adc = ADC5V()

    while True:
        try:
            a = float(input('n: '))
            dac.voltage = a
        except ValueError:
            a = 'NaN'
        print('dac set to {a}, adc_raw reads: {b}, converted: {c}'.format(
            a=a, b=adc.read_raw(), c=adc.voltage))
        time.sleep(0.1)
