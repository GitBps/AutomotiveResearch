#				Automotive Research and Analytics 
##		Method and Apparatus to analyzing Road Quality

## Background

Maps have become significant part of our day to day lives. It is the best friend while driving and also when someone wants to find the way to any desitination. Google maps, Street views and also a lot of other advancements are happening as we speak. 

Maps provides us the options like 
1) Search for a destination and select the paths (generally the shortest)
2) Change the path dynamically based on say, traffic or late traffic indications
3) Provides us an ETA based on instantaneous traffic load and path selected
4) Others

This is all based on the data avaialble at the given time on the servers, and also due to the maps uploading the information from User's phone to the servers. The data is from the phones, and if the user dont use phones, there is no way to understand the live data. 

**But what maps doesnt provide us today is the road condition - as in, it doesnt let us select the road based on road conditions- and this is the basis of the current literature** 


## Problem Statement 

Maps dont provide us the following option and that becomes our **"Problems to Solve"**

- [X] *Road conditions (like the bumps,holes,roads torn due to repairs)*
- [X] *Reason for the Jams: If there is a jam because of bad road(s) / due to repair work/ say some vehicle Stranded*
- [X] *It cant give information regarding say the engine vibrations* 
- [X] *Also it cant give information regarding say, the tyre's abnormality due to long usage*
- [X] *Analytics over localized data (and would be more accurate)*
  - *Automatic feeding of the data by several vehicles into dynamic database(to be updated by each passing vehicle)*
  - *Future usage of this data by other vehicles, who have chosen this path*
  

## Implementation Details 

The proposal here is divided into the following Functional details  
1) Attach Accelerometers to the moving parts of the vehicle (front engine/wheels and/or rear wheels)
2) Attach a GPS Module to the vehicle ideally towards one center of the vehicle
3) Create a local IP Network between these devices and the end router with NW Upload capability

The configuration of the devices are as below => 
<img src = https://github.com/GitBps/AutomotiveResearch/blob/master/SensorGPSProject/Snapshots/OverallFunctionalDiagram.png >

Here the data collection source is not the Mobile Phone but the real Sensors connected to the User's vehicle.Data collection at source is REALTIME and once accurately available, it is used offline by all users without even participating in the overall collection. In that way it is a first hand information available directly from the hardware sources.

## Tools and technologies used

### Hardware tools

**Rapberry Pi (rapbian OS) X2**: is built on a single circuit board with microprocessor, memory, I/O and other features primarily for educational purposes. Operating System used is Raspbian OS (Linux Distribution).

**Wifi dongle**: For pi2, we used wifi dongle to connect with mobile broadband(4G).

**Soldering equipment**: Soldering equipments were used to permanently glue sensors to the jumper wires.

**ADXL345 accelerometer X2**: It is a small, low power, 3-axis accelerometer with 13 bit resolution that measures the dynamic acceleration due to motion. Digital output data is accessible through either I2C or SPI digital interface.

**GPS module**: GPS module is used to detect the Latitude and Longitude of any location with exact time. It sends data related to tracking position in real time in NMEA format.

### Software tools

**InfluxDB**: It is an open source database optimized for fast, high-availability storage and retrieval of time series data. In our case, all the sensor data is stored in InfluxDB in real time.

**Grafana Labs**: It is an analytics tool that allows to query, visualize and understand any metrics from the stored data. In our case, we used Grafana to plot the time-series data and the geolocation of the anomalies in time-series data from InfluxDB in the inbuilt mapping tool for visualization.


## Basic Setup and Working Details (How it is implemented)

a) As seen in the previous sections, there are sensor data which will be typically a short string format of 30 odd bytes and is coming at a frequency of every **500ms**. 

- This looks something like this for each sensor 
  - <SensorId = Id, X = x, Y = y, Z = z>


b) There is also a GPS Data coming to the Sensor Device every **1 second** and it contains atleast 9-10 strings carrying the following data strings 

- $GPRMC,134809.00,A,1254.29859,N,07738.82074,E,0.178,,300419,,,A*79
- $GPVTG,,T,,M,0.178,N,0.330,K,A*2D
- **$GPGGA,134809.00,1254.29859,N,07738.82074,E,1,03,2.94,940.5,M,-86.6,M,,*75**
- $GPGSA,A,2,12,05,25,,,,,,,,,,3.11,2.94,1.00*0F
- $GPGSV,3,1,11,02,28,029,16,05,63,034,39,06,01,056,17,12,74,245,25*74
- $GPGSV,3,2,11,13,24,138,,15,23,176,18,19,12,105,08,21,05,268,*77
- $GPGSV,3,3,11,24,15,205,09,25,44,306,19,29,19,329,*44
- $GPGLL,1254.29859,N,07738.82074,E,134809.00,A,A*61

Each string has its own significance. 

### Detection of Network Latencies

The above collection of data is sent out every second (**almost accurately**) and reaches the **Central Controller** with some network and processing latency. 

**Considering the GPS Clocks coming as PPS every second (Measured accurately), we are planning to use it as a SYNCHRONIZATION MECHANISM for any out of time packets at the central service. **


<img src = https://github.com/GitBps/AutomotiveResearch/blob/master/SensorGPSProject/Snapshots/FunctionalBlock2.png >





