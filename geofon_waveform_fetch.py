import os
import pandas as pd
import numpy as np

from obspy.core import UTCDateTime
from obspy.clients.fdsn.client import FDSNNoDataException, Client

if __name__ == "__main__":

    #FILE PATHS
    main_path = os.path.dirname(os.path.abspath(__file__))
    event_file_path = os.path.join(main_path, 'earthquakes.txt')

    #EVENT FILTERING
    events = pd.read_csv(event_file_path, sep='\s+')
    events.insert(loc = 0, column= "event_ID", value = range(0, events.shape[0]))

    events = events[events['ident.'] != 'NN'] #drop all NN events - unidentified events
    events['ident.'] = np.where(events['ident.'] == 'MI', 1, 0) #change mining events to category 1, else it is category 0
    events.insert(loc = 0, column= "event_id", value = range(0, events.shape[0])) #insert new event id column

    #RENAME THE COLUMN HEADERS
    events.rename(columns={'Year': 'year',
                            'lat(WGS84)': 'lat',
                            'lng(WGS84)' : 'lng',
                            'depth[km]': 'depth',
                            'mag.[ML]' : 'mag_ML',
                            'ML-std-dev': 'std_dev_ML',
                            'mag.[MA],': 'mag_MA',
                            'MA-std-dev,': 'std_dev_MA',
                            'ident.': 'category'}, inplace = True)

    #FETCH GEOFON  DATA
    GEOFON_client = Client("GEOFON")
    network_code = "GE"
    station_code = "LVC"
    channel_code = "BH*" #B (broad band, high sample rate 10-80 Hz); H(weak motion sensor - e.g. velocity); Z, 1, 2 (single component sensor)
    location_code = "10" #reserved for weak motion sensors
    dt = 60 #we take waveform in the span of 1 min before and after the event time stamp


    #WE ITERATE THROUGH OUR EVENTS
    start_row = 0
    end_row = len(events)
    for idx, row in events.iloc[start_row:end_row,:].iterrows(): #iterate through events
        time_stamp = UTCDateTime(int(row['year']),
                                 int(row['month']), 
                                 int(row['day']),
                                 int(row['hour']),
                                 int(row['minute']),
                                 float(row['second']))
        t1 = time_stamp - 60
        t2 = time_stamp + 60
            
        try:
            #FETCHING THE WAVEFORM FROM OBSPY
            waveform = GEOFON_client.get_waveforms(network = network_code,
                                                    station = station_code,
                                                    location = location_code,
                                                    channel = channel_code,
                                                    starttime = t1,
                                                    endtime = t2)
            
            #SAVING THE FILE AS MSEED FILE
            waveform_file_name = f"{int(row['event_id'])}.mseed"
            waveform_file_path = os.path.join(main_path, 'geofon_waveforms', waveform_file_name)
            waveform.write(waveform_file_path, format = "MSEED")

            print(f"Created file {waveform_file_name} for event at {time_stamp}")

        except FDSNNoDataException:
            events.drop(index=idx, inplace=True) #if we couldnt find the waveform for the given event we remove it from our dataframe
            print(f"No available data from GEOFON for event {int(row['event_id'])} at {time_stamp}")


    #CREATE NEW TXT FILE WHICH CONTAINS ONLY THE EVENTS FOR WHICH WE HAVE THE WAVEFORMS
    new_file_path = os.path.join(main_path, 'earthquakes_geofon_filtered.txt')
    events.to_csv(new_file_path, sep=',')



