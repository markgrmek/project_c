import os
import pandas as pd
import numpy as np

from obspy.core import UTCDateTime
from obspy.clients.fdsn.client import FDSNNoDataException, Client

main_path = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":

    #PANDAS DATAFRAME--------------------------------------------------------------------------------------------------
    event_file_path = os.path.join(main_path, 'earthquakes.txt')
    events = pd.read_csv(event_file_path, sep='\s+')
    events.insert(loc = 0, column= "event_ID", value = range(0, events.shape[0]))

    events = events[events['ident.'] != 'NN'] #drop all NN events - unidentified events
    events['ident.'] = np.where(events['ident.'] == 'MI', 1, 0) #change mining events to category 1, else it is category 0
    events.insert(loc = 0, column= "event_id", value = range(0, events.shape[0])) #insert new event id column

        #rename column headers into nicer headers
    events.rename(columns={'Year': 'year',
                            'lat(WGS84)': 'lat',
                            'lng(WGS84)' : 'lng',
                            'depth[km]': 'depth',
                            'mag.[ML]' : 'mag_ML',
                            'ML-std-dev': 'std_dev_ML',
                            'mag.[MA],': 'mag_MA',
                            'MA-std-dev,': 'std_dev_MA',
                            'ident.': 'category'}, inplace = True)
    
    new_events_filepath = os.path.join(main_path, 'earthquakes_filtered.txt')
    events.to_csv(new_events_filepath, sep=',')

    #OBSPY PARAMETERS---------------------------------------------------------------------------------------------
    GEOFON_client = Client("GEOFON")
    network_code = "GE"
    station_code = "LVC"
    channel_code = 'BHZ, BHN, BHE' #B (broad band, high sample rate 10-80 Hz); H(weak motion sensor - e.g. velocity); Z, 1, 2 (single component sensor)
    channel_code_alt = 'BHZ, BH1, BH2'
    location_code = "10" #reserved for weak motion sensors
    dt = 60 #we take waveform in the span of 1 min before and after the event time stamp
    waveform_array_lenght = 4801 #stdard waveform array lenght

    #FILE PARAMETERS------------------------------------------------------------------------------------------------
    start_row = 4000 #the events before this had no data to provide - it saves some time
    end_row = len(events) #we go until the end
    files_created = 0
    desired_amount_of_files = 50000

    #EVENT ITERATION-------------------------------------------------------------------------------------------------
    for idx, row in events.iloc[start_row:end_row,:].iterrows(): #iterate through events
        if files_created < desired_amount_of_files:
            time_stamp = UTCDateTime(int(row['year']),
                                    int(row['month']), 
                                    int(row['day']),
                                    int(row['hour']),
                                    int(row['minute']),
                                    float(row['second']))
            t1 = time_stamp - 60
            t2 = time_stamp + 60
                
            try:
                #waveform fetching
                waveform = GEOFON_client.get_waveforms(network = network_code,
                                                        station = station_code,
                                                        location = location_code,
                                                        channel = channel_code,
                                                        starttime = t1,
                                                        endtime = t2)
                
                traces = [trace.data for trace in waveform]

                if (len(traces) == 3):
                    if (len(traces[0]) == len(traces[1]) == len(traces[2]) == waveform_array_lenght):

                        #writing to mseed file
                        waveform_file_name = f"{int(row['event_id'])}.mseed"
                        waveform_file_path = os.path.join(main_path, 'geofon_waveforms', waveform_file_name)
                        waveform.write(waveform_file_path, format = "MSEED")

                        files_created += 1

                        print(f"Created file {waveform_file_name} for event at {time_stamp}")

                else:   
                    try:
                        waveform = GEOFON_client.get_waveforms(network = network_code,
                                                        station = station_code,
                                                        location = location_code,
                                                        channel = channel_code_alt,
                                                        starttime = t1,
                                                        endtime = t2)
                
                        traces = [trace.data for trace in waveform]

                        if (len(traces) == 3):
                            if (len(traces[0]) == len(traces[1]) == len(traces[2]) == waveform_array_lenght):

                                #writing to mseed file
                                waveform_file_name = f"{int(row['event_id'])}.mseed"
                                waveform_file_path = os.path.join(main_path, 'geofon_waveforms', waveform_file_name)
                                waveform.write(waveform_file_path, format = "MSEED")

                                files_created += 1

                                print(f"Created file {waveform_file_name} for event at {time_stamp}")
                            
                            else:
                                print(f"Event {int(row['event_id'])} at {time_stamp} doesnt have array of same lenghts")
                        else:
                            print(f"Event {int(row['event_id'])} at {time_stamp} had a direction missing")

                    except FDSNNoDataException: #if we couldnt find the waveform for the given event
                        print(f"No available data for event {int(row['event_id'])} at {time_stamp}")
                        continue
                
            except FDSNNoDataException: #if we couldnt find the waveform for the given event
                print(f"No available data for event {int(row['event_id'])} at {time_stamp}")
                continue

        else:
            break



