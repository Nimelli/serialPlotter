# SerialPlotter
Python utility to plot data (typically data from sensors) coming from a serial port.

Useful for visualizing sensors data.

![Alt text](screenshot.png?raw=true "Screenshot")

## Installation

### Prerequisite

- PyQt5: needed for pyqtgraph
  
  pip: `pip install pyqt5`

  conda: `conda install pyqt`

- pyqtgraph: fast plotting api ([pyqtgraph.org](pyqtgraph.org))

  pip: `pip install pyqtgraph`

  conda: `conda install pyqtgraph`

- numpy: 
  
  pip: `pip install numpy`

  conda: `conda install -c anaconda numpy`

- pyserial:
  
  pip: `pip install pyserial`

  conda: `conda install pyserial`


## How to use it

### data message protocol

Incoming serial data must by in JSON format in the following form:

```json
{
    "Sensor":<sensorName>, 
    "TStamp":<timestamp>,
    "Data":{
        <sensorData>
    }
}
```

For example MPU6050 could be:
```json
{
    "Sensor":"MPU6050", 
    "TStamp":<timestamp>,
    "Data":{
        "AccX": <accX>,
        "AccY": <accY>,
        "AccZ": <accZ>
    }
}
```

### variables
- Set DEBUG_SERIAL to True to simulate a sensor readings. Set to False for normal operation.
- Change SERIAL_PORT, SERIAL_BAUDRATE to fit your serial settings.
- Change NB_OF_SIGNALS to fit your requirements


