import numpy as np
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe 
import json 
import pandas as pd



class Mqtt():
    def __init__(self,**kwargs):
        self.mqtt_client_name = kwargs["mqtt_client_name"] 
        self.mqtt_broker = kwargs["mqtt_broker"]
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id="peder")
        self.mqtt_client.username_pw_set(username=kwargs["username"],password=kwargs["password"])
        self.mqtt_client.connect(self.mqtt_broker,1883,60)

    def publish(self,topic,data):
        self.mqtt_client.publish(self.mqtt_client_name + topic,data)
        print("Published to topic: ",self.mqtt_client_name + topic)
    
    def subscribe(self,topic):
        subscribe.callback(self.on_message,topic,hostname=self.mqtt_broker,port=1883,auth = {"username": "ah","password": "komele"},)
        print("Subscribed to topic: ",self.mqtt_client_name + topic)

    def on_message(self,client,userdata,message):
        print("Message received on topic: ",message.topic)
        print("Message: ",str(message.payload.decode("utf-8")))
        return message.payload.decode("utf-8")
    


if __name__ == '__main__':
    mqtt = Mqtt(mqtt_client_name = "Solar",mqtt_broker = "192.168.1.12",username = "ah",password = "komele")
    #Open database.csv
    with open('database.csv') as csv_file:
        data = pd.read_csv(csv_file)
        #Convert to sting
        last_row = data.iloc[-1]
        data = data.to_json()
    mqtt.publish("/data",data)

    # Read the CSV file into a DataFrame
    df = pd.read_csv('first_value.csv', header=None)
    # Select the 3rd and 4th rows (index 2 and 3)
    selected_rows = df.iloc[2:4]
    selected_rows = selected_rows.round(2)
    print(selected_rows)
    #Append last_row[1] to selected_rows
    new_row = pd.DataFrame([[last_row[1]]], columns=[1])
    selected_rows = pd.concat([selected_rows, new_row], ignore_index=True)
    selected_rows = selected_rows.round(2)
    print(selected_rows)
    mqtt.publish("/first",selected_rows.to_json())

    q = mqtt.subscribe("/test")
    print(q)
    mqtt.mqtt_client.loop_forever()
    print("End")




