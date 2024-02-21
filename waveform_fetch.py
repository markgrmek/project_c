import os
import pandas as pd

from obspy.core import UTCDateTime
from obspy.clients.fdsn.client import FDSNNoDataException, Client


#FILE PATHS
directory_path = os.path.dirname(os.path.abspath(__file__))
event_file_path = os.path.join(directory_path, 'earthquakes.txt')

#EVENT FILTERING
events = pd.read_csv(event_file_path, sep='\s+')
events = events[events['ident.'] == 'MI'] #filter the events connected to mining blats (ident == MI)

#NARROWING DOWN THE AREA OF STATIONS
max_lat, min_lat = events['lat(WGS84)'].max(), events['lat(WGS84)'].min()
max_lng, min_lng = events['lng(WGS84)'].max(), events['lng(WGS84)'].min()
max_year, min_year = events['Year'].max(), events['Year'].min()

max_year = UTCDateTime(max_year,12,31, 0,0,0)
min_year = UTCDateTime(min_year, 1, 1, 0,0,0)


#EXPLANATION ON CODES FOR RETRIEVEING WAVEFORMS
"""https://www.geonet.org.nz/data/supplementary/channels"""


#GEOFON AND IRIS NETWORK STATIONS
"""
data on available at: 
https://geofon.gfz-potsdam.de/waveform/archive/station.php

https://geoserver.iris.edu/content/85432
"""


#FETCH GEOFON  DATA
    #fixed parameters
GEOFON_client = Client("GEOFON")
IRIS_client = Client("IRIS")

channel_code = "BHZ" #B (broad band, high sample rate 10-80 Hz); H(weak motion sensor - e.g. velocity); Z (single component vertical sensor)
location_code = "10" #reserved for weak motion sensors

dt = 60 #we take waveform in the span of 1 min before and after the event time stamp

#GET NETWORKS AND STATIONS DATA

    #GEOFON
GEOFON_inventory = GEOFON_client.get_stations(maxlatitude = max_lat,
                                        minlatitude = min_lat,
                                        maxlongitude = max_lng,
                                        minlongitude = min_lng,
                                        startafter=min_year,
                                        endbefore=max_year,
                                        level = "station")

    #we create a list of tuples that contains the a network with the corresponding stations
GEOFON_network_station_tuple_list = []
for network in GEOFON_inventory:   #iterate through networks
    for station in network: #iterate through stations
        GEOFON_network_station_tuple_list.append((network.code, station.code))

    #IRIS
IRIS_inventory = IRIS_client.get_stations(maxlatitude = max_lat,
                                    minlatitude = min_lat,
                                    maxlongitude = max_lng,
                                    minlongitude = min_lng,
                                    startafter=min_year,
                                    endbefore=max_year,
                                    level = "station")
    
    #we create a list of tuples that contains the a network with the corresponding stations
IRIS_network_station_tuple_list = []
for network in IRIS_inventory:   #iterate through networks
    for station in network: #iterate through stations
        IRIS_network_station_tuple_list.append((network.code, station.code))



#WE ITERATE THROUGH OUR EVENTS
start_row = 10
end_row = 11
for idx, row in events.iloc[start_row:end_row,:].iterrows(): #iterate through events
    time_stamp = UTCDateTime(row['Year'], row['month'], row['day'], row['hour'], row['minute'], row['second'])
    t1 = time_stamp - 60
    t2 = time_stamp + 60

    for networks_station_tup in GEOFON_network_station_tuple_list:
        network_code = networks_station_tup[0]
        station_code = networks_station_tup[1]
        
        try:
            waveform = GEOFON_client.get_waveforms(network = network_code,
                                                    station = station_code,
                                                    location = location_code,
                                                    channel = channel_code,
                                                    starttime = t1,
                                                    endtime = t2)
            
            waveform_file_name = f"{row['Year']}_{row['month']}_{row['day']}_{row['hour']}_{row['minute']}_{row['second']}_GEOFON_{network_code}_{station_code}_{location_code}_{channel_code}"
            waveform.write(waveform_file_name, format = "MSEED")
            print(f"Created {waveform_file_name}")

        except FDSNNoDataException:
            print(f"No available data from GEOFON for {time_stamp} - {network_code}; {station_code}; {location_code}")

    
    for networks_station_tup in IRIS_network_station_tuple_list:
        network_code = networks_station_tup[0]
        station_code = networks_station_tup[1]
        
        try:
            waveform = IRIS_client.get_waveforms(network = network_code,
                                                    station = station_code,
                                                    location = location_code,
                                                    channel = channel_code,
                                                    starttime = t1,
                                                    endtime = t2)
            
            waveform_file_name = f"{row['Year']}_{row['month']}_{row['day']}_{row['hour']}_{row['minute']}_{row['second']}_IRIS_{network_code}_{station_code}_{location_code}_{channel_code}"
            waveform.write(waveform_file_name, format = "MSEED")
            print(f"Created {waveform_file_name}")
            
        except FDSNNoDataException:
            print(f"No available data frpm IRIS for {time_stamp} - {network_code}; {station_code}; {location_code}")



