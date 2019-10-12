from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure



from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.uic import loadUi


from pymeasure.instruments.srs import SR830

import sys


class dummy:
    """dummy context manager doing nothing at all"""

    def __init__(self):
        pass

    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        pass



# class Window_ui(QtWidgets.QWidget):
#     """Class for a small window, the UI of which is loaded from the .ui file
#     emits a signal when being closed
#     """

#     sig_closing = pyqtSignal()

#     def __init__(self, ui_file=None, **kwargs):
#         if 'lock' in kwargs:
#             del kwargs['lock']
#         super().__init__(**kwargs)
#         if ui_file is not None:
#             loadUi(ui_file, self)
#         # self.setWindowIcon(QtGui.QIcon('TU-Signet.png'))

#     def closeEvent(self, event):
#         """emit signal that the window is going to be closed and hand event to parent class method"""
#         self.sig_closing.emit()
#         # event.accept()  # let the window close
#         super().closeEvent(event)


# class Window_plotting(QtWidgets.QDialog, Window_ui):
#     """Small window containing a plot, which updates itself regularly"""
#     sig_closing = pyqtSignal()

#     def __init__(self, data, label_x, label_y, legend_labels, number, title='your advertisment could be here!', **kwargs):
#         """storing data, building the window layout, starting timer to update"""
#         super().__init__(**kwargs)
#         self.data = data
#         self.label_x = label_x
#         self.label_y = label_y
#         self.title = title
#         self.legend = legend_labels
#         self.number = number
#         if 'lock' in kwargs:
#             self.lock = kwargs['lock']
#         else:
#             self.lock = dummy()

#         self.interval = 0.1

#         # a figure instance to plot on
#         self.figure = Figure()

#         # this is the Canvas Widget that displays the `figure`
#         # it takes the `figure` instance as a parameter to __init__
#         self.canvas = FigureCanvas(self.figure)

#         # this is the Navigation widget
#         # it takes the Canvas widget and a parent
#         self.toolbar = NavigationToolbar(self.canvas, self)

#         # Just some button connected to `plot` method
#         # self.button = QtWidgets.QPushButton('Plot')
#         # self.button.clicked.connect(self.plot)

#         # set the layout
#         layout = QtWidgets.QVBoxLayout()
#         layout.addWidget(self.toolbar)
#         layout.addWidget(self.canvas)
#         # layout.addWidget(self.button)
#         self.setLayout(layout)
#         self.lines = []
#         self.plot_base()

#         self.timer = QTimer()
#         self.timer.timeout.connect(self.plot)
#         self.timer.start(self.interval * 1e3)

#     def plot_base(self):
#         """create the first plot"""

#         self.ax = self.figure.add_subplot(111)
#         self.ax.set_title(self.title)
#         self.ax.set_xlabel(self.label_x)
#         self.ax.set_ylabel(self.label_y)

#         # discards the old graph
#         if not isinstance(self.data, list):
#             self.data = [self.data]
#         self.ax.clear()
#         # print(self.data)
#         with self.lock:
#             for entry, label in zip(self.data, self.legend):
#                 ent0, ent1 = shaping(entry)
#                 self.lines.append(self.ax.plot(
#                     ent0, ent1, '*-', label=label)[0])
#         self.ax.legend()

#     def plot(self):
#         ''' update the plotted data in-place '''
#         try:
#             with self.lock:
#                 for ct, entry in enumerate(self.data):
#                     ent0, ent1 = shaping(entry)
#                     self.lines[ct].set_xdata(ent0)
#                     self.lines[ct].set_ydata(ent1)
#             self.ax.relim()
#             self.ax.autoscale_view()
#             self.canvas.draw()
#         except ValueError as e_val:
#             print('ValueError: ', e_val.args[0])

#     def closeEvent(self, event):
#         """stop the timer for updating the plot, super to parent class method"""
#         self.timer.stop()
#         super().closeEvent(event)
#     #     del self

		

if __name__ == '__main__':
	lockin1 = SR830('GPIB::9')

	data = [lockin1.x, lockin1.y]

    app = QtWidgets.QApplication(sys.argv)
    form = Window_plotting(data, 'X', 'Y', 'something', 1)
    form.show()
    sys.exit(app.exec_())

	while True:
		data[0] = lockin1.x
		data[1] = lockin1.y


