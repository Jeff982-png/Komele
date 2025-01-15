import numpy as np
import prophet as pt
from prophet.plot import plot_plotly, plot_components_plotly  
import matplotlib.pyplot as plt   
import pandas as pd
import json
import os
import tracemalloc
import time


#Import custom module
from get_json import Solar

class Prediction():
    def __init__(self,siteid,type,start_time,end_time,meters,api_key,name,period,print_info = False):
        #Info to get it in the program 
        self.siteid = siteid
        self.type = type
        self.start_time = start_time
        self.end_time = end_time
        self.meters = meters
        self.api_key = api_key
        self.name = name
        self.print = print_info
        self.data = None

        #Dataset from solatrEdge
        self.s = Solar()
        #Generate data from SolarEdge API and create files based on name
        d = self.s.request(self.siteid,self.type,self.start_time,self.end_time,self.meters,self.api_key,self.name)[0]
        self.model = pt.Prophet()
        self.forecast = None
        self.period = period
        self.name = name
        self.df = None
        self.prediction = None
        self.read_data()
        self.predict()
        
    def read_data(self): 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_found = False
        for root, dirs, files in os.walk(dir_path):
            for file in files: 
                if file == self.name + '.csv':
                    print ('Opening: '+root+'/'+str(file))
                    file_found = True
                    with open(root+'/'+str(file), encoding='utf-8') as csv_file:
                        self.data = pd.read_csv(csv_file)
                        if self.data.shape[1] != 2:
                            raise ValueError('The csv file should have 2 columns')
            if not file_found:
                raise ValueError('No csv files found in the directory')     

    def predict(self):
        self.model.fit(self.data)
        future = self.model.make_future_dataframe(periods=self.period*96,freq = '15min') # 96 periods per day for 15-minute intervals
        self.forecast = self.model.predict(future)
        self.prediction = self.forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        if self.print:
            self.model.plot(self.forecast)
            plt.show()
            print(self.prediction)
            print('Finished prediciton')
            return
        else:
            print('Finished prediciton')
            return

    def set_new_time(self):
        start_time = self.end_time
        x = start_time.split("%20",1)
        y = x[0].split("-")
        z = int(y[2]) + self.period
        if z < 10:
            z = '0'+str(z)
        else:
            z = str(z)   
        new_time = y[0]+'-'+y[1]+'-'+z+'%20'+x[1]

        return new_time
        
    def compare(self, end_time, return_data = False):
        start_time = end_time
        end_time = self.set_new_time()
        prev_pred = self.prediction #Get the prediciton based on out model input data
        #Extract only the prediction data from prev_pred
        prev_pred_filtered = self.filter_pred(start_time,end_time)#ds/yhat/yhat_lower/yhat_upper
        name = "compare"
        c = Prediction(self.siteid,self.type,start_time,end_time,self.meters,self.api_key,name,self.period)
        
        # Ensure 'ds' columns are datetime
        prev_pred_filtered.loc[:, 'ds'] = pd.to_datetime(prev_pred_filtered['ds'])
        c.data.loc[:, 'ds'] = pd.to_datetime(c.data['ds'])
        
        merged_data = pd.concat([prev_pred_filtered.set_index('ds'), c.data.set_index('ds')], axis=1).reset_index()
        merged_data = merged_data.infer_objects() #IDK ? Becasue of warning ?
        merged_data['difference'] = merged_data['y'] - merged_data['yhat']

        # Plot the data
        plt.figure(figsize=(14, 4))
        plt.subplot(2,1,1)
        plt.plot(merged_data['ds'], merged_data['yhat'], label='Predicted', color='blue')
        plt.plot(merged_data['ds'], merged_data['y'], label='Actual', color='orange')
        plt.fill_between(merged_data['ds'], merged_data['yhat_lower'], merged_data['yhat_upper'], color='blue', alpha=0.2)
        plt.legend()
        plt.xlabel('Date')
        plt.ylabel('Poraba W')
        plt.title('Predicted vs Actual Values')
        plt.subplot(2,1,2)
        plt.plot(merged_data['ds'], merged_data['difference'], label='Difference', color='red')
        plt.legend()
        plt.xlabel('Date')
        plt.ylabel('Difference W (Actual - Predicted)')
        plt.title('Difference between Predicted and Actual Values')
        plt.show()
        #save to csv onyl the first data of predict and the first of compare
        first_row = merged_data.iloc[0][['ds', 'yhat', 'difference']]
        first_row.to_csv('first_value.csv', index=False)

        if return_data:
            return merged_data

    def filter_pred(self,start,end):
        start = start.replace("%20"," ")
        end = end.replace("%20"," ")
        print("start:", start)
        print("end: ", end)
        if self.prediction is not None and isinstance(self.prediction, pd.DataFrame):
            mask = (self.prediction['ds'] >= start) & (self.prediction['ds'] <= end)
            filtered_prediction = self.prediction.loc[mask]
            return filtered_prediction
        else:
            raise ValueError('Prediction data is not available or not a DataFrame')

if __name__ == '__main__':
    start_time = time.time()
    tracemalloc.start()

    #Dictionary for the model
    model = {   
        "siteid": '4466261',
        "type": 'powerDetails',
        "start_time": '2024-11-14%2011:00:00',
        "end_time": '2024-12-02%2013:00:00',
        "meters": 'CONSUMPTION',
        "api_key": 'MLK3N9SFEN0UHJV3MCNISYFAO126AACA',
        "name": 'database',
        "period": 2,
    }

    #Generate data into csv file by set parameters
    #Predict the data for the set period
    p = Prediction(**model)	
    c = p.compare(model['end_time'],True)
    end_time = time.time()

    print("Time elapsed: ", end_time - start_time)
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    for stat in top_stats[:10]:
        print(stat)
    



    
    
    