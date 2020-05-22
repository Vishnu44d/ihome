import paho.mqtt.client as mqtt
import sys
from influxdb import InfluxDBClient
import json

## COnnection from the postgres database
from dbConnect import DbEngine_config, create_db_engine, create_db_sessionFactory
engine = create_db_engine(DbEngine_config)
SessionFactory = create_db_sessionFactory(engine)
SQLSession = create_db_sessionFactory(engine)

def on_connect(client, userdata, flags, rc):    
    print("Result from connect: {}".format(
            mqtt.connack_string(rc)))    
    # Subscribe to the all topic
    from topics import topics
    for topic in topics:
        client.subscribe(topic)

def on_subscribe(client, userdata, mid, granted_qos):    
    print("I've subscribed")

def write_db(payload):
    try:
        influx_client.write_points(payload)
        print("Data write done!")
    except Exception as e:
        print("Error writting ", str(e))


def on_message(client, userdata, msg):   
    ## insert data into database
    ## chck for topic, if not cmd then write
    ## if any device is sending it's status then write to postgresql db
    ## otherwise write to influx db

    topic = msg.topic
    super_topic = topic.split("/")[0]
    if super_topic == "sensors":
        # write into influxDB
        write_db(json.loads(msg.payload))
    elif super_topic == "status":
        # update the status of the device in postgresDB

        try:
            session = SQLSession()
            ## update the status of device in postgres
            session.close()
        except Exception as e:
            
            print(str(e))
    print("Message received. Topic: {}. Payload: {}".format(
            msg.topic, str(msg.payload)))
    
    

def on_disconnect(client, userdata, rc):
    print("Reconnecting")
    client.connect(host="mqtt", port=1883)


if __name__ == "__main__":    
    client = mqtt.Client(protocol=mqtt.MQTTv311)    
    client.on_connect = on_connect    
    client.on_subscribe = on_subscribe    
    client.on_message = on_message
    client.on_disconnect = on_disconnect    
    client.connect(host="mqtt", port=1883)  
    dbname="ihome"
    host="influx"
    port=8086
    influx_client = InfluxDBClient(host=host, port=port)
    influx_client.switch_database(dbname)  
    client.loop_forever()