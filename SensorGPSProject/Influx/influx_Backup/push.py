# -*- coding: utf-8 -*-
"""Tutorial how to use the class helper `SeriesHelper`."""

import time
from influxdb import InfluxDBClient
from influxdb import SeriesHelper
import socket

# InfluxDB connections settings
host = 'localhost'
port = 8086
user = 'root'
password = 'root'
dbname = 'mydb'

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
        fields = ['x', 'y', 'z']

        # Defines all the tags for the series.
        tags = ['server_name']

        # Defines the number of data points to store prior to writing
        # on the wire.
        bulk_size = 5

        # autocommit must be set to True when using bulk_size
        autocommit = True




#for var in list(range(5000)):
#    MySeriesHelper(server_name='us.east-1',x=10 + var,y=210,z=662)
#    time.sleep(2) 
#    result = myclient.query('select "x" FROM  "events.stats.us.east-1"')
#    print("Result: {0}".format(result))

# Create a socket object
s = socket.socket()

# Define the port on which you want to connect
port = 8877

# Next bind to the port
# we have not typed any ip in the ip field
# instead we have inputted an empty string
# this makes the server listen to requests
# coming from other computers on the network
s.bind(('', port))
print ("socket binded to %s" %(port))

# put the socket into listening mode
s.listen(5)
print ("socket is listening")

# a forever loop until we interrupt it or
# an error occurs
# Establish connection with client.
c, addr = s.accept()
print ('Got connection from', addr)

import re

while True:
    # receive data from the server
    #sensorId, x, y, z = c.recv(1024)
    s= str(c.recv(1024))
    data = re.split('=|,', s)
    # close the connection
    print(data)
    print(data[1] + data[3] + data[5] + data[7])

    #MySeriesHelper(server_name='us.east-1', s=str(data[1]), x= int(data[3]), y=int(data[5]), z=int(data[7][:-1]))
    MySeriesHelper(server_name='us.east-1', x= int(data[3]), y=int(data[5]), z=int(data[7][:-1]))
    #MySeriesHelper(server_name='us.east-1', s=2328, x=3232 , y=322, z=32)
    
s.close()
c.close()











# To manually submit data points which are not yet written, call commit:
MySeriesHelper.commit()


# To inspect the JSON which will be written, call _json_body_():
MySeriesHelper._json_body_()

