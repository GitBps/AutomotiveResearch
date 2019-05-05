# -*- coding: utf-8 -*-
"""Tutorial how to use the class helper `SeriesHelper`."""

import time
from datetime import datetime
from influxdb import InfluxDBClient
from influxdb import SeriesHelper
from threading import Lock
import array as arr
import socket
import re
import math

#Internal Variable used in code
diff = 0
delta = 0
val = 0
bump =0
currentIndex = 0
currentZcoord = arr.array('i', [0, 0,0,0])
lastZcoord = arr.array('i', [0, 0,0,0])


# InfluxDB connections settings
host = 'localhost'
port = 8086
user = 'root'
password = 'root'
dbname = 'mylocationdb'
sname = 'unndefined'
mutex = Lock()

myclient = InfluxDBClient(host, port, user, password, dbname)
myclient.create_database(dbname)

class MySeriesHelper(SeriesHelper):
    """Instantiate SeriesHelper to write points to the backend."""

    class Meta:
        """Meta class stores time series helper configuration."""

        # The client should be an instance of InfluxDBClient.
        client = myclient

        # The series name must be a string. Add dependent fields/tags
        # in curly brackets.
        series_name = 'events.stats.{server_name}'

        # Defines all the fields in this time series.
        fields = ['server_name', 'key', 'lat', 'lon', 'metric', 'name']

        # Defines all the tags for the series.
        tags = ['servername']

        # Defines the number of data points to store prior to writing
        # on the wire.
        bulk_size = 5

        # autocommit must be set to True when using bulk_size
        autocommit = True


class MyAcclerometer(SeriesHelper):
    """Instantiate SeriesHelper to write points to the backend."""

    class Meta:
        """Meta class stores time series helper configuration."""

        # The client should be an instance of InfluxDBClient.
        client = myclient

        # The series name must be a string. Add dependent fields/tags
        # in curly brackets.
        series_name = 'events.stats.{server_name}'

        # Defines all the fields in this time series.
        #fields = ['x', 'y', 'z']
        fields = ['z']

        # Defines all the tags for the series.
        tags = ['server_name']

        # Defines the number of data points to store prior to writing
        # on the wire.
        bulk_size = 5

        # autocommit must be set to True when using bulk_size
        autocommit = True

def latitudeToDecimal (lat, dir):
    if (lat != "" and dir != ""):
        minutes = float(lat[2:10])
        degrees = float(lat[0:2])
        print ("Degrees = {0}, Minutes {1}".format(degrees, minutes))
        degrees = degrees + minutes/60
        if (dir == "S"):
            degrees = -degrees
        return float(degrees)
    else:
        return float(0)

def longitudeToDecimal (lat, dir):
    if (lat != "" and dir != ""):
        minutes = float(lat[3:11])
        degrees = float(lat[0:3])
        print ("Degrees = {0}, Minutes {1}".format(degrees, minutes))
        degrees = degrees + minutes/60
        if (dir == "W"):
            degrees = -degrees
        return float(degrees)
    else:
        return float(0)


def setGPSLatLon(line):
    global latitude, longitude
    print(line)
    receivedString = re.split('=|,', line)
    print("GGA DATA")
    print (receivedString[0], receivedString[1], receivedString[2], receivedString[3], receivedString[4])
    print (receivedString[5], receivedString[6], receivedString[7], receivedString[8])
    lat = latitudeToDecimal(receivedString[5], receivedString[6])
    latitude = float(lat)     
    print ("LAT : {0}".format(latitude))
    longi = longitudeToDecimal(receivedString[7], receivedString[8])
    longitude = float(longi)
    print ("LON : {0}".format(longitude))

# Create a socket object
s = socket.socket()

# Define the port on which you want to connect
port = 8877
s.bind(('', port))
print ("socket binded to %s" %(port))
s.listen(5)
print ("socket is listening")
c, addr = s.accept()
print ('Got connection from', addr)

lastSentFix = datetime.now()
while True:
    # receive data from the server
    mutex.acquire()
    s= str(c.recv(1024))

    #print("[START *********] Updated GPS Fix")
    #print(s)
    #print("[END ***********] Updated GPS Fix")
    data = re.split('=|,', s)
    # close the connection

    print(data[1])
    #time.sleep(0.5) 

    if (data[1] == "S1"):
        sname = "us.east-1"
        currentIndex = 0
    elif (data[1] == "S2"):
        sname = "us.east-2"
        currentIndex = 1
    elif (data[1] == "G1"):
        sname = "us.east-1"
        setGPSLatLon(s)
        mutex.release()
        continue
    else:
        continue

    print("sname: {0}".format(sname))
 
    print(data[1] + " " +  data[3] + " " + data[5] + " "  + data[7] + " " + str(lastZcoord[currentIndex]))
    currentZcoord[currentIndex] = int(data[7][:-1])
    if (currentZcoord[currentIndex] >= lastZcoord[currentIndex]):
        diff = currentZcoord[currentIndex] - lastZcoord[currentIndex]
    else: 
        diff = lastZcoord[currentIndex] - currentZcoord[currentIndex]

    lastZcoord[currentIndex] = currentZcoord[currentIndex]


    if (diff > 5):
        global latitude, longitude
        MyAcclerometer(server_name = sname, z=int(lastZcoord[currentIndex]))
        diff = 0;
        currentTime = datetime.now()
        # check when was the last timestamp we had sent Location
        # skip if not > 0.5 seconds.
        delta = currentTime - lastSentFix
        deltaMillis = (delta.days * 86400000) + (delta.seconds * 1000) + (delta.microseconds / 1000)
        print("BUMP: {0} LAT {1} LON {2}".format(bump, latitude , longitude ))

        if (deltaMillis >= 100 and latitude !=0 and longitude != 0):
            #MySeriesHelper( server_name=sname, key='SE', lat=20.6 +val , lon=78.643501 +val, metric = 1,name='sweden',  servername='us.east-1')
            MySeriesHelper( server_name="us.east-1", key='SE', lat= latitude + val , lon= longitude + val, metric = 1,name='sweden',  servername='us.east-1')
            lastSentFix = datetime.now()
            latitude = 0 
            longitude = 0
        bump = bump + 1
    else:
        bump = 0
        #val = val +0.001# assuming 40KMPH - 1 degree will be travelled in 9000 seconds.

    mutex.release()


s.close()
c.close()

# To manually submit data points which are not yet written, call commit:
MyAcclerometer.commit()
MySeriesHelper.commit()
# To inspect the JSON which will be written, call _json_body_():
MySeriesHelper._json_body_()
MyAcclerometer._json_body_()

