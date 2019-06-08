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

DEBUG_SERIAL    = True
NB_OF_SIGNALS   = 10
VERBOSE         = True

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'SerialPlotter'
        self.left = 200
        self.top = 100
        self.width = 1080
        self.height = 720

        self.plt = pg.PlotWidget()
        self.signals = []
        for i in range(0,NB_OF_SIGNALS):
            self.signals.append(self.plt.plot())

        self.s1XData = np.array([])
        self.s1YData = np.array([])

        self.rxQueue = queue.Queue()
        self.txQueue = queue.Queue()
        self.serThread = SerialThread(self.rxQueue, self.txQueue, 'COM4', 9600, debug=DEBUG_SERIAL) # default port and baudrate
        self.serThread.start()

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


    def update(self):
        # update loop

        # read rxQueue
        while self.rxQueue.qsize():
            try:
                msg = self.rxQueue.get()
                msg_str = msg.decode("utf-8")

                msg_obj = json.loads(msg_str)

                if(VERBOSE):                        
                    print(msg_obj["Sensor"])
                
                #self.s1YData = np.append(self.s1YData, float(msg_str))
                #self.s1XData = np.append(self.s1XData, self.s1YData.shape[0])
            except:
                pass

        # update signals
        #self.signals[0].setData(self.s1XData, self.s1YData)

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())