import json, requests
import pandas as pd
import numpy as np
import os


class Solar():    
    def request(self, siteid,type,start_time, end_time, meters,api_key,name):
        req = 'https://monitoringapi.solaredge.com/site/' + siteid + '/'+ type + '?meters=' + meters + '&startTime=' + start_time + '&endTime=' + end_time + '&api_key=' + api_key
        print(req)
        self.raw = requests.get(req)
        self.raw = self.raw.json()
        self.type = type
        #Save to raw_data.json
        self.name = name
        with open(self.name + '.json', 'w') as outfile:
            json.dump(self.raw, outfile) 

        self.convert() #Convert to csv with name saved in self.file

        return self.raw,req
    
    def convert(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        json_file_found = False
        for root, dirs, files in os.walk(dir_path):
            for file in files: 
                if file == self.name + '.json':
                    print ('Converting: '+root+'/'+str(file))
                    json_file_found = True
                    with open(root+'/'+str(file), encoding='utf-8') as json_file:
                        data = json.load(json_file)
                        # Extract date and values
                        meter_telemetries = data.get(self.type, {}).get('meters', [])[0].get('values', [])
                        dates = [entry['date'] for entry in meter_telemetries if 'date' in entry]
                        values = [entry.get('value', np.nan) for entry in meter_telemetries]
                        # Create DataFrame
                        data_frame = {
                            'ds': dates,
                            'y': values
                        }
                        df = pd.DataFrame(data_frame)
                        file = file.replace('.json', '')
                        df.to_csv(file + '.csv', index=False)

                    self.file = str(file)+'.csv'   
                    print('Converted to: '+str(file)+'.csv')  
                    #Print the number of rows and columns
                    print('Rows: '+str(df.shape[0])+' Columns: '+str(df.shape[1]))              
            if not json_file_found:
                raise ValueError('No json files found in the directory')     
        return      
