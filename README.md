# Installation
To install
```
pip3 install -e . --user
```


# Setup
To prepare a new data set run:
```
source env.sh
```
This sets up a directory for the current date at ``data/YYYY_MM_DD/``.


# Commands
After setting up, a number of helpful aliases and environment variables are set.


## Camera
To display the camera on the current raspberry pi monitor (connect to display 0
over vnc, if connected remotely), run
```
camera-preview <digital zoom factor, optional>
```

To capture a series of still images, run
```
camera-capture <n stills> <ms between stills>
```
These images can be found in the ``data/YYYY_MM_DD/img_HH_MM_SS/`` directory,
labelled by the unix timestamp.


## Pressure gauge
Currently the pressure gauge is logged manually. However, the
```
pg-run
```
command will log (and timestamp) pressure data entered into a prompt.

Output data files can be found at ``data/YYYY_MM_DD/PG_<timestamp>.h5``.


## RTD
Drizzle has an external chip for a single 4-wire rtd set up and read out via
spi. The command
```
rtd-run
```
will set up the RTD chip and start logging data to
``data/YYYY_MM_DD/RTD_<timestamp>.h5``.


## Capacitive level sensor
LArBo is instrumented with a slim capacitive level sensor, read out via an
Arduino. The Arduino periodically sends data over a serial usb connection. The
```
levelsensor-run --port /dev/<usb port, typically ttyACM0>
```
command begins the levelsensor logger.

Data can be found at ``data/YYYY_MM_DD/LS_<timestamp>.h5``.


## ADC
Drizzle also has an external 4-channel 16-bit ADC. Two channels of which are
used to measure a discrete liquid level sensor. To begin logging ADC data, run
```
adc-run
```

Data can be found at ``data/YYYY_MM_DD/ADC_<timestamp>.h5``.


## Data monitor
```
monitor-run
```
plots the most recent logged data from the sensors within the current data set,
updated periodically. This command should be run from a terminal with an
attached display, so if connecting remotely, you will need to start a second vnc
server or run from the desktop vnc connection.
