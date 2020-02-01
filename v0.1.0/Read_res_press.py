# from LakeShore350 import LakeShore350
import argparse
import pandas as pd
# import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import datetime

from pymeasure.instruments.keithley import Keithley2000

from util import LS350
from util import measure_tempres
from util import measure_pressure_multimeter
# from util import pressure


# import logging
# # import sys

# log = logging.getLogger()
# log.setLevel(logging.DEBUG)

# logexc = logging.getLogger('exceptions')
# logexc.setLevel(logging.DEBUG)

# handler2 = logging.FileHandler('logexc.log', mode='a')
# handler2.setLevel(logging.INFO)
# handler = logging.FileHandler('log.log', mode='a')
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter(
#     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# handler2.setFormatter(formatter)
# log.addHandler(handler)
# logexc.addHandler(handler2)


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
    parser.add_argument('-pcs1', "--pressure_cross_section_a", type=float, default=argparse.SUPPRESS,
                        help="one side of cross-section for pressure")
    parser.add_argument('-pcs2', "--pressure_cross_section_b", type=float, default=argparse.SUPPRESS,
                        help="one side of cross-section for pressure")
    parser.add_argument('-i', "--interval", type=int, default=argparse.SUPPRESS,
                        help="time interval between measurements [seconds]")
    args = parser.parse_args()
    datafile = args.file

    if all(name in args for name in ('cross_section_a', 'cross_section_b', 'length')):
        cs1 = args.cross_section_a
        cs2 = args.cross_section_b
        length = args.length
    else:
        cs1 = cs2 = length = 1e3

    if all(name in args for name in ('pressure_cross_section_a', 'pressure_cross_section_b')):
        pcs1 = args.pressure_cross_section_a
        pcs2 = args.pressure_cross_section_b
    else:
        pcs1 = pcs2 = 1e3

    BESSY_OCT_2019 = dict(cs1=2.9, cs2=0.58, length=0.24, pcs1=0.58, pcs2=0.24)

    SAMPLE_DIMENSIONS = dict(
        cs1=cs1, cs2=cs2, length=length, pcs1=pcs1, pcs2=pcs2)
    SAMPLE_DIMENSIONS.update(BESSY_OCT_2019)

    if 'interval' in args:
        timeinterval = args.interval
    else:
        timeinterval = 1  # this corresponds to 1 measurement / second

    df = pd.DataFrame(
        dict(time=[], temp=[], tempres=[], rho=[], resistivity=[], read_pressure=[], read_pvoltage=[], pressure_sample=[]))

    LS = LS350(None, 'GPIB::9::INSTR')
    KTmult = Keithley2000('GPIB::14::INSTR')
    KTmult.measure_voltage(max_voltage=10, ac=False)

    fig = plt.figure()
    grid = gridspec.GridSpec(2, 2, figure=fig)

    ax1 = fig.add_subplot(grid[0, 0])
    ax1.set_xlabel("T (K)")
    ax1.set_ylabel(r"$\rho$ ($\Omega$ m)")
    ax1.ticklabel_format(axis='y', style='sci', scilimits=(0, 2))
    line0, = ax1.plot(df['temp'], df['rho'], 'k.-')

    ax2 = fig.add_subplot(grid[1, 0])
    ax2.set_xlabel("time")
    # ax2.set_ylabel(r"$\rho$ ($\Omega$ m)")
    ax2.set_ylabel(r"R ($\Omega$)")
    ax2.ticklabel_format(axis='y', style='sci', scilimits=(0, 2))
    line1, = ax2.plot_date(df['time'], df['rho'], 'k.-')

    ax3 = fig.add_subplot(grid[0, 1])
    ax3.set_xlabel("pressure in cell [bar]")
    ax3.set_ylabel(r"$\rho$ ($\Omega$ m)")
    ax3.ticklabel_format(axis='y', style='sci', scilimits=(0, 2))
    line2, = ax3.plot(df['read_pressure'], df['rho'], 'k.-')

    ax4 = fig.add_subplot(grid[1, 1])
    ax4.set_xlabel("pressure in sample [MPa]")
    ax4.set_ylabel(r"$\rho$ ($\Omega$ m)")
    ax4.ticklabel_format(axis='y', style='sci', scilimits=(0, 2))
    line3, = ax4.plot(df['pressure_sample'], df['rho'], 'k.-')

    plt.tight_layout()

    while True:

        data = dict(time=datetime.datetime.now())

        LSdata = measure_tempres(LS, SAMPLE_DIMENSIONS)
        data_pressure = measure_pressure_multimeter(KTmult)

        data.update(LSdata)
        data.update(data_pressure)

        df = df.append(data, ignore_index=True)

        with open(datafile, 'a', newline='') as f:
            df.tail(1).to_csv(f, header=f.tell() == 0)

        line0.set_xdata(df['temp'])
        line1.set_xdata(df['time'])
        line2.set_xdata(df['read_pressure'])
        line3.set_xdata(df['pressure_sample'])
        # line3.set_xdata(df['read_pressure'])
        for line in [line1, line0, line2, line3]:
            line.set_ydata(df['rho'])
        # line1.set_ydata(df['rho'])

        for a in [ax1, ax2, ax3, ax4]:
            a.relim()
            a.autoscale_view()

        plt.draw()
        plt.pause(timeinterval)
