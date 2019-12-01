import paho.mqtt.client as mqtt
import sys
from influxdb import InfluxDBClient


def on_connect(client, userdata, flags, rc):    
    print("Result from connect: {}".format(
            mqtt.connack_string(rc)))    
# Subscribe to the senors/alitmeter/1 topic filter 
    client.subscribe("sensors/thermometer/1")     



def on_subscribe(client, userdata, mid, granted_qos):    
    print("I've subscribed")

def write_db(payload):
    dbname="ihome"
    host="influx"
    port=8086
    influx_client = InfluxDBClient(host=host, port=port)
    influx_client.switch_database(dbname)
    return influx_client.write_points(payload)




def on_message(client, userdata, msg):   
    ## insert data into database
    #write_db(msg.payload)
    print("Message received. Topic: {}. Payload: {}".format(
            msg.topic, str(msg.payload)))



if __name__ == "__main__":    
    client = mqtt.Client(protocol=mqtt.MQTTv311)    
    client.on_connect = on_connect    
    client.on_subscribe = on_subscribe    
    client.on_message = on_message    
    client.connect(host="mqtt", port=1883)    
    client.loop_forever()