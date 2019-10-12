from LakeShore350 import LakeShore350
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import datetime


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
    args = parser.parse_args()
    datafile = args.file

    if all(name in args for name in ('cross_section_a', 'cross_section_b', 'length')):
        cs1 = args.cross_section_a
        cs2 = args.cross_section_b
        length = args.length
    else:
        cs1 = cs2 = length = 1e3

    df = pd.DataFrame(
        dict(time=[], temp=[], tempres=[], rho=[], resistivity=[]))

    LS = LS350(None, 'GPIB::1::INSTR')

    SAMPLE_DIMENSIONS = dict(cs1=cs1, cs2=cs2, length=length)

    fig = plt.figure()
    grid = gridspec.GridSpec(2, 1, figure=fig)
    ax1 = fig.add_subplot(grid[0, :])
    ax1.set_xlabel("T (K)")
    ax1.set_ylabel(r"$\rho$ ($\Omega$ m)")
    ax1.ticklabel_format(axis='y', style='sci', scilimits=(0, 2))
    line0, = ax1.plot(df['temp'], df['resistivity'], 'k.-')
    ax2 = fig.add_subplot(grid[1, :])
    ax2.set_xlabel("time")
    ax1.set_ylabel(r"$\rho$ ($\Omega$ m)")
    ax2.ticklabel_format(axis='y', style='sci', scilimits=(0, 2))
    line1, = ax2.plot_date(df['time'], df['resistivity'], 'k.-')
    # line2, = ax2.plot(df['ch2r'], df['temp'], 'b.-', label='Ch. 2')

    plt.tight_layout()

    while True:

        rho = LS.sensB

        df = df.append(dict(time=datetime.datetime.now(), rho=rho,
                            temp=LS.tempA, tempres=LS.sensA, resistivity=geomfactor(**SAMPLE_DIMENSIONS) * rho), ignore_index=True)

        with open(datafile, 'a', newline='') as f:
            df.tail(1).to_csv(f, header=f.tell() == 0)

        line0.set_xdata(df['temp'])
        line1.set_xdata(df['time'])
        for line in [line1, line0]:
            line.set_ydata(df['resistivity'])

        for a in [ax1, ax2]:
            a.relim()
            a.autoscale_view()

        plt.draw()
        plt.pause(30)
