import paho.mqtt.client as mqtt
from flask_cors import CORS
from ihomeback.models import createTables, destroyTables
from ihomeback.config import DbEngine_config
from ihomeback import create_db_engine, create_db_sessionFactory
from ihomeback.api import deviceBP
from ihomeback.api import userBP
import os
from flask import Flask
import json
import random
import sys
sys.path.insert(0, os.getcwd())
# from flask_mqtt import Mqtt


app = Flask(__name__)
engine = create_db_engine(DbEngine_config)
# destroyTables(engine)
# createTables(engine)

SessionFactory = create_db_sessionFactory(engine)
SQLSession = create_db_sessionFactory(engine)

app.config['MQTT_BROKER_URL'] = 'mqtt'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEP_ALIVE'] = 5
# app.config['MQTT_REFRESH_TIME'] = 1.0

# mqtt = Mqtt(app)

# @mqtt.on_connect()
# def handle_connect(client, userdata, flags, rc):
#     print("Connecting...")
#     mqtt.subscribe('sensors/thermometer/1')


def on_connect(client, userdata, flags, rc):
    print("Result from connect: {}".format(
        mqtt.connack_string(rc)))
    # Subscribe to the senors/alitmeter/1 topic filter
    from topics import topics
    for topic in topics:
        client.subscribe(topic)


def on_subscribe(client, userdata, mid, granted_qos):
    print("I've subscribed")


def on_message(client, userdata, msg):
    # insert data into database

    print("Message received. Topic: {}. Payload: {}".format(
        msg.topic, str(msg.payload)))


def on_disconnect(client, userdata, rc):
    print("Reconnecting")
    client.connect(host="mqtt", port=1883)


client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_disconnect = on_disconnect
client.connect(host="mqtt", port=1883)


CORS(app, supports_credentials=True)
@app.route('/', methods=['GET'])
def root():
    try:
        json_body = [
            {
                "measurement": "temperature",
                "tags": {
                    "host": "server0{}".format(random.randint(1, 4))
                },
                "fields": {
                    "value": random.randint(30, 60),
                }
            }
        ]
        client.publish("sensors/thermometer/1",
                       json.dumps(json_body)).wait_for_publish()
        json_body = [
            {
                "measurement": "humidity",
                "tags": {
                    "host": "server{}".format(random.randint(1, 4))
                },
                "fields": {
                    "value": random.randint(80, 100),
                }
            }
        ]
        client.publish("sensors/humidity/1",
                       json.dumps(json_body)).wait_for_publish()
        return "<h1>Hello</h1>"
    except Exception as e:
        print(str(e))
        return "<h1>World</h1>"


app.register_blueprint(userBP, url_prefix='/user')
app.register_blueprint(deviceBP, url_prefix='/device')

if __name__ == "__main__":
    print("Starting the backend server")
    app.run(host="0.0.0.0", use_reloader=False)
    client.loop_forever()
