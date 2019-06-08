import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout,
                            QTextEdit, QLineEdit, QCheckBox, QComboBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer


import pyqtgraph as pg
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

import numpy as np
import threading
import queue
from SerialThread import SerialThread
from math import sin
import json
import colorsys

DEBUG_SERIAL    = True
VERBOSE         = True
NB_OF_SIGNALS   = 10

def get_N_HexCol(N=5):
    HSV_tuples = [(x * 1.0 / N, 0.5, 0.5) for x in range(N)]
    hex_out = []
    for rgb in HSV_tuples:
        rgb = map(lambda x: int(x * 255), colorsys.hsv_to_rgb(*rgb))
        hex_out.append('#%02x%02x%02x' % tuple(rgb))
    return hex_out


penColors = get_N_HexCol(NB_OF_SIGNALS)
print(penColors)


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'SerialPlotter'
        self.left = 200
        self.top = 100
        self.width = 1080
        self.height = 720

        # plots variables
        self.plt = pg.PlotWidget()
        self.signals = []
        self.signalsDataX = []
        self.signalsDataY = []
        for i in range(0,NB_OF_SIGNALS):
            self.signals.append(self.plt.plot(pen=pg.mkPen(penColors[i], width=3)))
            self.signalsDataX.append(np.array([]))
            self.signalsDataY.append(np.array([]))

        self.signalAssigned = np.zeros([NB_OF_SIGNALS], dtype=bool)
        self.sensorDataToIdx = {}

        # serial thread
        self.rxQueue = queue.Queue()
        self.txQueue = queue.Queue()
        self.serThread = SerialThread(self.rxQueue, self.txQueue, 'COM4', 9600, debug=DEBUG_SERIAL) # default port and baudrate
        self.serThread.start()

        # timer to call update() undefinitely
        self.updateTimer = QTimer(self)
        self.updateTimer.setInterval(10)
        self.updateTimer.timeout.connect(self.update)

        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createLayout()
        self.show()
        self.updateTimer.start()

    def createLayout(self):
        mainGrid = QGridLayout()
        mainGrid.setSpacing(10)

        # PLot
        self.plotGroupBox = QGroupBox("Plots")

        mainGrid.addWidget(self.plotGroupBox)

        plotLayout = QVBoxLayout()
        plotLayout.addWidget(self.plt)
        self.plotGroupBox.setLayout(plotLayout)

        self.setLayout(mainGrid)

    def closeEvent(self, event):
        print('Stopping serial thread')
        self.serThread.stopSignal = True
        if(self.serThread.running):
            self.serThread.join()

        self.updateTimer.stop()
        print('Closing')
        event.accept() # let the window close

    def assignDataToSignal(self, key):
        # function used to assignal a particular data stream to a signal plot

        # count how many signal are not already assigned
        lefts = np.nonzero(self.signalAssigned==0)[0]
        if(lefts.size == 0):
            print('Error: no more signals left')
            return -1
        else:
            # assign to first available signal
            idx = lefts[0] # first left
        
            self.signalAssigned[idx] = True
            self.sensorDataToIdx[key] = idx
            print('key: {}, idx: {}'.format(key, idx))
            return idx

    def getSignalIndex(self, key):
        # function used to retreive ti signal plot index based on the data name (key)
        if (key in self.sensorDataToIdx.keys() ):
            # key is already assigned
            return self.sensorDataToIdx[key]
        else:
            return self.assignDataToSignal(key)


    def update(self):
        # update loop

        # read rxQueue
        while self.rxQueue.qsize():
            try:
                msg = self.rxQueue.get()
                msg_str = msg.decode("utf-8")

                msg_obj = json.loads(msg_str)

                if(VERBOSE):                        
                    print(msg_obj)

                sensorName = msg_obj["Sensor"]
                sensorData = msg_obj["Data"]

                for key in sensorData.keys():
                    compoudKey = sensorName + '_' + key
                    idx = self.getSignalIndex(compoudKey)

                    self.signalsDataY[idx] = np.append(self.signalsDataY[idx], sensorData[key])
                    self.signalsDataX[idx] = np.append(self.signalsDataX[idx], msg_obj["TStamp"])
                
            except:
                pass

        # update signals
        for i in range(0,NB_OF_SIGNALS):
            self.signals[i].setData(self.signalsDataX[i], self.signalsDataY[i])

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())