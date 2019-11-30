import os
from flask import Flask
import json
from flask_mqtt import Mqtt

app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = 'mqtt'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 1.0

mqtt = Mqtt(app)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("Connecting...")
    mqtt.subscribe('sensors/thermometer/1')



@app.route('/', methods=['GET'])
def root():
    try:
        pub_data = {"data1": "value1"}
        mqtt.publish("sensors/thermometer/1", json.dumps(pub_data))
        return "<h1>Hello</h1>"
    except:
        return "<h1>World</h1>"

if __name__ == "__main__":
    print("Starting the server")
    app.run(host='0.0.0.0', port=os.environ.get("FLASK_PORT", "80"))