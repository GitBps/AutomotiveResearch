#!/usr/bin/env python
import time
import serial
import datetime
import socket

ser = serial.Serial(
 port='/dev/ttyAMA0',
 baudrate = 9600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)
counter=0

# Create a socket object
s = socket.socket()
# Define the port on which you want to connect
port = 12345
sensorId = "G1"

# connect to the server on local computer
s.connect(('127.0.0.1', port))
    # receive data from the server
   
while 1:
 x=ser.readline()
 if (x.startswith('$GPGGA')):
	print "GPGGA SENT"
	s.send('S={0},X={1}'.format(sensorId,x))
	print s.recv(1024)
 else:
	print "NON GPGGA - NOT SENT"
	print x

 # close the connection
    
s.close()
