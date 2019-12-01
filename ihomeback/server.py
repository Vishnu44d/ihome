import os
from flask import Flask
import json
# from flask_mqtt import Mqtt

app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = 'mqtt'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEP_ALIVE'] = 5
# app.config['MQTT_REFRESH_TIME'] = 1.0

# mqtt = Mqtt(app)

# @mqtt.on_connect()
# def handle_connect(client, userdata, flags, rc):
#     print("Connecting...")
#     mqtt.subscribe('sensors/thermometer/1')

import paho.mqtt.client as mqtt
import sys

def on_connect(client, userdata, flags, rc):    
    print("Result from connect: {}".format(
            mqtt.connack_string(rc)))    
# Subscribe to the senors/alitmeter/1 topic filter 
    client.subscribe("sensors/thermometer/1")     

def on_subscribe(client, userdata, mid, granted_qos):    
    print("I've subscribed")


def on_message(client, userdata, msg):   
    ## insert data into database

    print("Message received. Topic: {}. Payload: {}".format(
            msg.topic, str(msg.payload)))


client = mqtt.Client(protocol=mqtt.MQTTv311)    
client.on_connect = on_connect    
client.on_subscribe = on_subscribe    
client.on_message = on_message    
client.connect(host="mqtt", port=1883)
 


@app.route('/', methods=['GET'])
def root():
    try:
        pub_data = {"data1": "value1"}
        json_body = [
            {
                "measurement": "temperature",
                "tags": {
                    "host": "server01"
                },
                "fields": {
                    "value": 90,
                }
            }
        ]
        client.publish("sensors/thermometer/1", json.dumps(json_body)).wait_for_publish()
        return "<h1>Hello</h1>"
    except Exception as e:
        print(str(e))
        return "<h1>World</h1>"

if __name__ == "__main__":
    print("Starting the server")
        
    client.loop_forever()
    app.run(host='0.0.0.0', port=os.environ.get("FLASK_PORT", "80"), debug=False, use_reloader=False)