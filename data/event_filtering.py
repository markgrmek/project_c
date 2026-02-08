import os
import pandas as pd
import numpy as np

main_path = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    #PANDAS DATAFRAME--------------------------------------------------------------------------------------------------
    event_file_path = os.path.join(main_path, 'earthquakes.txt')
    events = pd.read_csv(event_file_path, sep='\s+')
    events.insert(loc = 0, column= "event_id", value = range(0, events.shape[0]))

    events = events[events['ident.'] != 'NN'] #drop all NN events - unidentified events
    events['ident.'] = np.where(events['ident.'] == 'MI', 1, 0) #change mining events to category 1, else it is category 0

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
    events.to_csv(new_events_filepath, sep=',', index=False)