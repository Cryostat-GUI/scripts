import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import pandas as pd
# import numpy as np
import argparse

window_length = 50

fig = plt.figure()
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(2, 1, 2)
file = "data/EUG27A_p_caxis2.csv"


# parser = argparse.ArgumentParser()
# parser.add_argument('-f', "--file", type=str,
#                     help="filename for data storage", required=True)

# args = parser.parse_args()
# file = str(args.file, "utf-8")


def animate(i):
    # with open(file,"r") as f:
    #     pullData = f.read()

    df = pd.read_csv(file, parse_dates=['time'])
    # dataArray = pullData.split('\n')
    # df = pd.DataFrame(dataArray)
    roll = df.loc[:, df.columns != 'time'].rolling(window_length).mean()

    # a0ar = []
    # a1ar = []
    # a2ar = []
    # a3ar = []
    # a4ar = []
    # a5ar = []
    # a6ar = []
    # a7ar = []
    # a8ar = []
    # a9ar = []

    # for eachLine in dataArray:
    #     if len(eachLine)>1:
    #         a0,a1,a2,a3,a4,a5,a6,a7,a8,a9 = eachLine.split()
    #         a0ar.append(float(a0))
    #         a1ar.append(float(a1))
    #         a2ar.append(float(a2))
    #         a3ar.append(float(a3))
    #         a4ar.append(float(a4))
    #         a5ar.append(float(a5))
    #         a6ar.append(float(a6))
    #         a7ar.append(float(a7))
    #         a8ar.append(float(a8))
    #         a9ar.append(float(a9))
    ax1.clear()
    # ax1.plot(a0ar,a4ar, 'o')
    ax1.plot(df['set_pressure'], df['resistivity'], 'o', color='b')
    ax1.plot(roll['set_pressure'], roll['resistivity'], '-', color='r')
    # overwrite the x-label added by `psd`
    ax1.set_ylabel('Sample voltage (V)')
    ax1.set_xlabel('Pressure (bar)')  # overwrite the x-label added by `psd`
    ax2.clear()
    ax2.plot(df['resistivity'], 'o', color='b')
    ax2.plot(roll['resistivity'], '-', color='r')
    ax2.set_xlabel('Measurement no.')  # overwrite the x-label added by `psd`
    ax2.set_ylabel('Sample voltage (V)')  # overwrite the x-label added by `p


animate(50)
ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
