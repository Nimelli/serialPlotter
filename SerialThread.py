import threading
import queue
import serial
import time

class SerialThread(threading.Thread):
    def __init__(self, rxQueue, txQueue,  port, baudrate, debug=False):
        threading.Thread.__init__(self)
        self.rxQueue = rxQueue
        self.txQueue = txQueue
        self.stopSignal = False
        self.running = False
        self.port = port
        self.baud = baudrate
        self.debug = debug
    def run(self):
        self.running = True
        if(not self.debug):
            ser = serial.Serial(self.port, self.baud)
            while(not self.stopSignal):
                if ser.inWaiting():
                    #text = ser.readline(ser.inWaiting())
                    text = ser.readline()
                    self.rxQueue.put(text)

                while self.txQueue.qsize():
                    try:
                        cmd = self.txQueue.get()
                        cmd += '\r\n'
                        cmd_bytes = cmd.encode('utf-8')
                        print(cmd_bytes)
                        ser.write(cmd_bytes)
                    except Queue.Empty:
                        pass
            ser.close()
        else:
            n = 0
            while(not self.stopSignal):
                time.sleep(0.01)
                self.rxQueue.put(str(n).encode('utf-8'))
                # print('Serial Thread: ' + str(n))
                n+=0.1
                if(n>=10):
                    n = 0
        self.running = False  