# Simple demo of of the ADXL345 accelerometer library.  Will print the X, Y, Z
# axis acceleration values every half second.
# Author: Tony DiCola
# License: Public Domain
import time

# Import socket module
import socket

# Import the ADXL345 module.
import Adafruit_ADXL345

# Create an ADXL345 instance.
accel = Adafruit_ADXL345.ADXL345()

# Alternatively you can specify the device address and I2C bus with parameters:
#accel = Adafruit_ADXL345.ADXL345(address=0x54, busnum=2)

# You can optionally change the range to one of:
#  - ADXL345_RANGE_2_G   = +/-2G (default)
#  - ADXL345_RANGE_4_G   = +/-4G
#  - ADXL345_RANGE_8_G   = +/-8G
#  - ADXL345_RANGE_16_G  = +/-16G
# For example to set to +/- 16G:
#accel.set_range(Adafruit_ADXL345.ADXL345_RANGE_16_G)

#accel.set_data_rate(Adafruit_ADXL345.ADXL345_DATARATE_6_25HZ)

# Create a socket object
s = socket.socket()

# Define the port on which you want to connect
port = 12345
sensorId = "S1"

# connect to the server on local computer
s.connect(('127.0.0.1', port))
print('Printing X, Y, Z axis values, press Ctrl-C to quit...')
while True:
    # Read the X, Y, Z axis acceleration values and print them.
    x, y, z = accel.read()
    print('sensor={0}, X={1}, Y={2}, Z={3}'.format(sensorId, x, y, z))
    s.send('S={0}, X={1}, Y={2}, Z={3}'.format(sensorId, x, y, z))
    # Wait half a second and repeat.
    time.sleep(0.6)

    # receive data from the server
    print s.recv(1024)
    # close the connection
    
s.close()



