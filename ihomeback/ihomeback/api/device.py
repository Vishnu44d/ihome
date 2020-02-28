from flask import request, Blueprint, jsonify
from ihomeback.models.deviceModel import Device
from ihomeback.auth.auth import validate_token


deviceBP = Blueprint('deviceApi', __name__)

@deviceBP.route('/test', methods=['GET'])
def get_me_my_humidity():
    from influxdb import InfluxDBClient
    dbname="ihome"
    host="influx"
    port=8086
    influx_client = InfluxDBClient(host=host, port=port)
    influx_client.switch_database(dbname)
    a = influx_client.query('SELECT * FROM humidity;')
    print(a)
    return jsonify({"data": list(a.get_points(measurement="humidity"))}), 200

@deviceBP.route('/', methods=['GET'])
def devices():
    '''
        1. take input as the token
        2. return all devices and there information. Query the status of the device too.
    '''
    try:
        auth = request.args.get('auth', None, type=str)
        print("auth = ", auth)
    except:
        response={
            "status":"fail",
            "messahe":"No argument"
        }
        return jsonify(response), 400
    if(validate_token({"token":auth})):
        from server import SQLSession
        session = SQLSession()
        devices = session.query(Device).all()
        res = [{
            "name": device.name,
            "port": device.port,
            "location": device.location,
            "desc": device.desc,
            "status": device.status
            } for device in devices]
        response = {
            "status": "success",
            "message": "device information",
            "payload": res
        }
        return jsonify(response), 200
    else:
        response = {
            "status": "fail",
            "message": "authorization fail"
        }
        return jsonify(response), 300


    
    

@deviceBP.route('/update', methods=['POST'])
def update_device():
    '''
        1. take the input as token, old device name, new device name.
        2. update in SQL database.
        3. return success or failure.
    '''

#######################################################################################
###################### CONTROLLING ####################################################
#######################################################################################

@deviceBP.route('/toggle', methods=['POST'])
def toggle_device():
    '''
        1. take input as token and name of device and future status to perform.
        2. publish this request as a topic for 'cmds/toggle/device_name'.
        3. return success or failure along with new status of device.
    '''
    data = request.json
    try:
        from server import client
        client.publish("cmd/thermometer/1", "ON").wait_for_publish()
        return jsonify({"msg": "published"}), 200
    except Exception as e:
        print(str(e))
        return jsonify({"msg": str(e)}), 500


@deviceBP.route('/intensity', methods=['POST'])
def change_intensity():
    '''
        1. take input as token and name of device and future intensity.
        2. publish this request as a topic for 'cmds/intensity/device_name'.
        3. return success or failure along with new intensity of device.
    '''

#######################################################################################
###################### MONITORING #####################################################
#######################################################################################

@deviceBP.route('/getrangedata', methods=['POST'])
def get_range_data():
    '''
        1. Take input as range (min, max, freq), token and device name.
        2. Query InfluxDB for this range data with the measurement as device name.
        3. return this data in json format.
    '''

@deviceBP.route('/getlatestdata', methods=['POST'])
def get_latest_data():
    '''
        1. Take input as token and device name.
        2. Query InfluxDB for latest entry.
        3. return this data in json format.
    '''