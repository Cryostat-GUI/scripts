from LakeShore350 import LakeShore350
import argparse
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import datetime

from pymeasure.instruments.srs import SR830


class LS350(LakeShore350):
    """docstring for LS350"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def sensA(self):
        return self.SensorUnitsInputReadingQuery('A')[0]

    @property
    def sensB(self):
        return self.SensorUnitsInputReadingQuery('B')[0]

    @property
    def tempA(self):
        return self.KelvinReadingQuery('A')[0]

    @property
    def tempB(self):
        return self.KelvinReadingQuery('B')[0]


def geomfactor(cs1, cs2, length):
    '''convert units (including sample geometries) so that [Ohm] becomes [Ohm m]
    cs1 and cs2 are the sides making up the cross-section:
        Area of cross section: A = cs1 * cs2
    length is the length of the path the current takes, as in:
    R = \rho * Length / A
    \rho = R * A / Length
    all units to be given in [mm]
    for other units ([Ohm cm]), the unit conversion
        needs to be applied 'inversly'
        [Ohm m] to [Ohm cm] has a factor of 1e2
    returns: factor to be applied to the resistance
    '''
    # area in mm^2
    Amm2 = cs1 * cs2
    # area in m^2
    Am2 = Amm2 * 1e-6
    # length in m
    le = length * 1e-3
    fac = Am2 / le
    return fac


def measure_tempres(LS):

    rho = LS.sensB

    return dict(rho=rho,
                temp=LS.tempA,
                tempres=LS.sensA,
                resistivity=geomfactor(**SAMPLE_DIMENSIONS) * rho)


def measure_pressure(SRlockin, goal_pressure, inlet_pressure, n):
    volt = goal_pressure / 1.7898
    # volt_max = inlet_pressure / 1.7898

    SRlockin.dac3 = volt
    time.sleep(1)

    for no_mes in range(n):
        read_voltage = SRlockin.adc3
        read_pressure = (read_voltage - 1.008) / 0.3924
        set_pressure = SRlockin.dac3 * 1.7898
        x = SRlockin.x
        y = SRlockin.y
        frequency = SRlockin.frequency
        sine_voltage = SRlockin.sine_voltage
        dac3 = SRlockin.dac3
        yield dict(set_pressure=set_pressure, read_pressure=read_pressure, dac3=dac3, read_voltage=read_voltage, x=x, y=y, frequency=frequency, sine_voltage=sine_voltage)

    # set_pressure = np.mean(np.array(set_pressure))
    # read_pressure = np.mean(np.array(read_pressure))
    # dac3 = np.mean(np.array(dac3))
    # read_voltage = np.mean(np.array(read_voltage))
    # x = np.mean(np.array(x))
    # y = np.mean(np.array(y))
    # frequency = np.mean(np.array(frequency))
    # sine_voltage = np.mean(np.array(sine_voltage))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', "--file", type=str,
                        help="filename for data storage", required=True)
    parser.add_argument('-cs1', "--cross_section_a", type=float, default=argparse.SUPPRESS,
                        help="one side of cross-section for resistivity")
    parser.add_argument('-cs2', "--cross_section_b", type=float, default=argparse.SUPPRESS,
                        help="one side of cross-section for resistivity")
    parser.add_argument('-l', "--length", type=float, default=argparse.SUPPRESS,
                        help="length for resistivity")
    parser.add_argument('-p', '--inlet', type=int, required=True,
                        help='pressure of the inlet')

    args = parser.parse_args()
    datafile = args.file
    inlet_pressure = args.inlet

    if all(name in args for name in ('cross_section_a', 'cross_section_b', 'length')):
        cs1 = args.cross_section_a
        cs2 = args.cross_section_b
        length = args.length
    else:
        cs1 = cs2 = length = 1e3

    df = pd.DataFrame(
        dict(time=[], temp=[], tempres=[], rho=[], resistivity=[], pressure=[],
             set_pressure=[], read_pressure=[], dac3=[], read_voltage=[], x=[], y=[], frequency=[], sine_voltage=[]))

    LS = LS350(None, 'GPIB::1::INSTR')
    lockin = SR830('GPIB::9')

    SAMPLE_DIMENSIONS = dict(cs1=cs1, cs2=cs2, length=length)
    print(df)

    for goal_pressure in range(1, 9, 1):

        if inlet_pressure < goal_pressure:
            raise AssertionError('Goal prressure exceeds the limit')

        ramp1 = np.linspace(0, goal_pressure, int(goal_pressure / 0.1))
        ramp2 = np.linspace(goal_pressure, 0, int(goal_pressure / 0.1))
        # print(ramp1)
        for ramp in (ramp1, ramp2):
            for voltage in ramp:

                for SRdata in measure_pressure(lockin, voltage, inlet_pressure, 50):
                    time.sleep(0.2)
                    data = dict(time=datetime.datetime.now(), pressure=0)

                    LSdata = measure_tempres(LS)
                    # SRdata = measure_pressure(SR830('GPIB::9'), voltage, args.inlet, 50)

                    data.update(LSdata)
                    data.update(SRdata)
                    df = df.append(data, ignore_index=True)
                    print(df.tail(1))
                    # rho = LS.sensB

                    # df = df.append(dict(time=datetime.datetime.now(), rho=rho,
                    # temp=LS.tempA, tempres=LS.sensA,
                    # resistivity=geomfactor(**SAMPLE_DIMENSIONS) * rho),
                    # ignore_index=True)

                    with open(datafile, 'a', newline='') as f:
                        df.tail(1).to_csv(f, header=f.tell() == 0)

                # line1.set_xdata(df['temp'])
                # line4.set_xdata(df['read_pressure'])
                # for line in [line2, line3]:
                #     line.set_xdata(df['time'])
                # for line in [line1, line2, line4]:
                #     line.set_ydata(df['resistivity'])

                # for a in [ax1, ax2, ax3, ax4]:
                #     # a.relim()
                #     a.autoscale_view()

                # plt.draw()
                # plt.pause(1)
