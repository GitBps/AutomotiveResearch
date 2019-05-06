#				Automotive Research and Analysis 
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

a) **ACCELEROMETER:** As seen in the previous sections, there are sensor data which will be typically a short string format of 30 odd bytes and is coming at a frequency of every **500ms**. 

- This looks something like this for each sensor **<SensorId = Id, X = x, Y = y, Z = z>**
- For each sensor ID the data would be the **absolute** displacement of the **X, Y, Z** coordintes.
- We prepend the sendor id to the coordinates so that we can distinguish the data came from which Sensor.

**Sensor data would not be plotted as it is, but rather be plotted only after Callibration and the time we updated the last coordinate**. This is explained in the **Callibration section** below

b) **GPGGA GPS LOCATION FIX:** There is also a GPS Data coming to the Sensor Device every **1 second** and it contains atleast 9-10 strings carrying the following data strings 

 - $GPRMC,134809.00,A,1254.29859,N,07738.82074,E,0.178,,300419,,,A*79
 - $GPVTG,,T,,M,0.178,N,0.330,K,A*2D
 - $GPGGA,134809.00,1254.29859,N,07738.82074,E,1,03,2.94,940.5,M,-86.6,M,,*75
 - $GPGSA,A,2,12,05,25,,,,,,,,,,3.11,2.94,1.00*0F
 - $GPGSV,3,1,11,02,28,029,16,05,63,034,39,06,01,056,17,12,74,245,25*74
 - $GPGSV,3,2,11,13,24,138,,15,23,176,18,19,12,105,08,21,05,268,*77
 - $GPGSV,3,3,11,24,15,205,09,25,44,306,19,29,19,329,*44
 - $GPGLL,1254.29859,N,07738.82074,E,134809.00,A,A*61

Each string has its own significance. But for the location details we need to parse the Latitude and Longitudes and convert them into the exact geolocations with negative and positive directions into considerations from the **GPGGA** String which comes in every Second. 

**GPGGA** string is parsed as shown in the below diagram for the details before handing that over to the Database and Grafanna for viewing.

<img src = https://github.com/GitBps/AutomotiveResearch/blob/master/SensorGPSProject/Snapshots/FunctionalBlock2.png >


## Challenge: Synchronization between various Nodes and GPS Module

Lets look at the proposals below to see the problem statement.

- **Proposal 1:** All devices publish their **data strings** directly to the **cloud**
  - **PROS:**
    - Easy design, easy implementation 
    - No dependency on any central device to collect, process, and publish
  - **CONS:**
    - No Synchronization of the frames, and @Database, frames would reach out of time
    - Lack of serialization
    - Network Delays could cause further issues, of wrong packets etc.

<img src = https://github.com/GitBps/AutomotiveResearch/blob/master/SensorGPSProject/Snapshots/LayoutProposal_1.png >

Proposal 1 looks easier but has serious drawbacks in terms of impact of data being plotted. 


- **Proposal 2:** Since all sensors have an IP, and the **Central Service** module is one which has Cloud connectivity it can manage much better all the data packets arriving from all sensors.
  - **PROS:**
    - Data fully Serialized 
    - Data processed more in the real time, Neglecting the Network Latencies.
    - Network Latencies can now be **DETECTED** (Proposal below) and out of time frames to be dropped to avoid wrong data
    - Latencies can be corrected before sending to the DB
    - A **Correction baed on time synchronization** Method is proposed below, and is **under implementation**
      (proposed in next section)
  - **CONS:** 
    - Central server needs to process all packets quite fast.
    - Measures to avoid Data corruption need be applied.

Proposal 2 looks promising as seen from the implementation perspective. This is the chosen implementation.

## Acclerometer/GPS Data Callibration and Filtering

- In general as seen in the setup the Accelerometer in discussion is a sensitive device and hence would generally **flood the database** if not filtered properly.
- Also noticed that during an upjerk or a downjerk, there would be multiple **INTERRUPTs from I2C** since the UP-DOWN cycle may take more than 500ms or sometimes even a second, **depending on the speed of the vehicle**
- GPS Sensor must show a dot on the map only if the such interrupt (as seen above) could be distintly counted and a sense of **time delta** from the last GPS Projection is done.

following is the flow, for both sensor and GPS to apply **Decided FILTERS**
<img src = https://github.com/GitBps/AutomotiveResearch/blob/master/SensorGPSProject/Snapshots/FlowChartFineTuning.png>

## Working Screenshots and DEMO

### S1 data + S2 Data + GPGGA Processed by Central Server

- Central server processing the data as received from the 2 sensors and the GPS Module.
- It does the **calibration and filters out** the measurements and then sends out the packet to influx

As seen in below image, this is a very fine tuned and callibrated details of sensor movements.
the Collector does a fair job in collecting published data, filters, and processes if filter criteria is met.

**Again Filter Criteria is subject to change based on how sensitive the Accelerometer data is requested**

<img src = https://github.com/GitBps/AutomotiveResearch/blob/master/SensorGPSProject/Snapshots/S1_S2_GPGGA.png >


### S1/S2 Moves, GPS criteria met, then its plotted.

1) Data coming from only 3 sensors 

The below is data from only sensors, plotted against the Influx timeline. this is plotted on real time as this arrives and meets the filter criteria. 

<img src = https://github.com/GitBps/AutomotiveResearch/blob/master/SensorGPSProject/Snapshots/OnlySensors.png>


2) Real time data from slow moving device in a small area to check for the accuracy of data in small intervals and with small population using this technology. 

**Data was accurately Published**

<img src = https://github.com/GitBps/AutomotiveResearch/blob/master/SensorGPSProject/Snapshots/integratedRealtime1.png >


3) When multiple users start to use this technique, then the data available would be much more consistent with reality. 
More over, as seen below the data is last 12 hrs of movement of device in places, and monitored several jerks at the locations plotted. 
As and when these locations are filled or repared, they would start to disappear
And data would be good for some of the **Future** users in time.

<img src = https://github.com/GitBps/AutomotiveResearch/blob/master/SensorGPSProject/Snapshots/PlotsLast12Hrs_1.png >

Another example of moving vehicle hitting 2+ disturbed areas and detected and plotted.
<img src =  https://github.com/GitBps/AutomotiveResearch/blob/master/SensorGPSProject/Snapshots/2Mapdots.png >

### Pulling Data from History 

Grafana has an inbuilt support for Influx connections, and due to that the committed data can be pulled back and plotted anytime. Data as old as 5 years could also be plotted. 

See below the configuration settings from Grafana

<img src = https://github.com/GitBps/AutomotiveResearch/blob/master/SensorGPSProject/Snapshots/GrafanaRefreshOption.png >

### FreeRunning Accelerometers - For Vehicle Health Detection

- This experiment could also be used to detect the health of the running vehicle - due to extra amounts of **Vibrations** from either the engine or the wheels. 
- Having known the baseline data, that the roads are good at a given location say in the given plots, then it can be clearly figured out that there is some wearing in the engine. 
- Moreover the data can be compared with historical data from same locations, to evaluate if there is a **degradation**

<img src = https://github.com/GitBps/AutomotiveResearch/blob/master/SensorGPSProject/Snapshots/FreeRunningWheelOrVibrationDetected.png>


## Detection & Correction Proposal for Network Latencies

**Problem Statement:** As explained in previous sections, since there are more than 5 differnet sensors here, who are all connected to the IP network and are pumping data strings every 500ms and 1 second respectively. 

On top of that there are network latencies and there are high amount of chances that if one of the network is delayed, data received would loose its real-timeliness and then be going wrongly.


The above collection of data is sent out every second (**almost accurately**) and reaches the **Central Controller** with some network and processing latency. 

**Considering the GPS Clocks coming as PPS every second (Measured accurately), we are planning to use it as a SYNCHRONIZATION MECHANISM for any out of time packets at the central service. **


**TODO: MSC FLOW TO BE EXPLAINED ON BOARD**

## Known Limitations and Remaining Tasks

- Mostly Realtime, Latencies not seen > 15-20 ms with 2-3 sensors and GPS with FIX.
- Network Latency could make things stale , things in above section to be implemented
- Influx query to be deviced for getting the counter value of number of hits by several users at a given GEO location so that it could be marked bad or good automatically based on the co-relation with latest data.
- **There is provision to add many more sensors this logic and many more use cases to be enabled with this as base** 

## GIT Path to Source Code and Snapshots

Full Source of Sensors, GPS, Central Server, Influx and Grafana details 
<img src = https://github.com/GitBps/AutomotiveResearch >

Grafana Hosted Dashboard 
<img src = https://grafanasnap.grafana.net/d/s401nZiZk/balvinder_plotted_finally?orgId=1&from=now-12h&to=now >

Influx + Python Programming Link
<img src = https://www.influxdata.com/blog/getting-started-python-influxdb/ >

Grafana Worldmap Panel
<img src = https://github.com/grafana/worldmap-panel>


#			End of the document



