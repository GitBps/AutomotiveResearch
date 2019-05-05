# -*- coding: utf-8 -*-
"""Tutorial how to use the class helper `SeriesHelper`."""

import time
from datetime import datetime
from influxdb import InfluxDBClient
from influxdb import SeriesHelper
import socket

# InfluxDB connections settings
host = 'localhost'
port = 8086
user = 'root'
password = 'root'
dbname = 'mylocationdb'

myclient = InfluxDBClient(host, port, user, password, dbname)

# Uncomment the following code if the database is not yet created
myclient.create_database(dbname)
# myclient.create_retention_policy('awesome_policy', '3d', 3, default=True)


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

import re
lastZcoord = 0
diff = 0
delta = 0

lastSentFix = datetime.now()
val = 0
bump =0
while True:
    # receive data from the server
    s= str(c.recv(1024))
    data = re.split('=|,', s)
    # close the connection

    #print(data)
    #print(data[1] + data[3] + data[5] + data[7])
    #time.sleep(0.5) 
    z=int(data[7][:-1])
    if (z >= lastZcoord):
        diff = z-lastZcoord
    else: 
        diff = lastZcoord - z

    lastZcoord = z;

    if (diff > 10):
        MyAcclerometer(server_name='us.east-1', z=int(lastZcoord))
        diff = 0;
        currentTime = datetime.now()
        # check when was the last timestamp we had sent Location
        # skip if not > 0.5 seconds.
        delta = currentTime - lastSentFix
        deltaMillis = (delta.days * 86400000) + (delta.seconds * 1000) + (delta.microseconds / 1000)
        print("BUMP: {0}".format(bump))
        if (deltaMillis >= 300):
            MySeriesHelper( server_name='us.east-1', key='SE', lat=20.6 +val , lon=78.643501 +val, metric = 1,name='sweden',  servername='us.east-1')
            lastSentFix = datetime.now()
        bump = bump + 1
    else:
        bump = 0
        val = val +0.001# assuming 40KMPH - 1 degree will be travelled in 9000 seconds.


#MyAcclerometer(server_name='us.east-2', x= int(data[3]), y=int(data[5]), z=int(data[7][:-1]))
#result = myclient.query('select "lat", "lon" FROM  "events.stats.us.east-1"')
#print("Result: {0}, Difference in Z:{1}".format(result, diff))
    
s.close()
c.close()

# To manually submit data points which are not yet written, call commit:
MyAcclerometer.commit()
MySeriesHelper.commit()
# To inspect the JSON which will be written, call _json_body_():
MySeriesHelper._json_body_()
MyAcclerometer._json_body_()

