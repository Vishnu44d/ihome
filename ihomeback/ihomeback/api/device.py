from flask import request, Blueprint, jsonify
from ihomeback.models.deviceModel import Device
from ihomeback.auth.auth import validate_token
import datetime

deviceBP = Blueprint('deviceApi', __name__)


@deviceBP.route('/test', methods=['GET'])
def get_me_my_humidity():
    from influxdb import InfluxDBClient
    dbname = "ihome"
    host = "influx"
    port = 8086
    influx_client = InfluxDBClient(host=host, port=port)
    influx_client.switch_database(dbname)
    a = influx_client.query('SELECT * FROM humidity;')
    print(a)
    return jsonify({"data": list(a.get_points(measurement="humidity"))}), 200


@deviceBP.route('/', methods=['GET'])
def devices():
    '''
        1. take input as the token in url
        2. return all devices and there information. Query the status of the device too.
    '''
    try:
        auth = request.args.get('auth', None, type=str)
        print("auth = ", auth)
    except:
        response = {
            "status": "fail",
            "messahe": "No argument"
        }
        return jsonify(response), 400
    if(validate_token({"token": auth})):
        from server import SQLSession
        session = SQLSession()
        devices = session.query(Device).all()
        session.close()
        res = [{
            "id": device.id,                        # id of device, for further query
            "name": device.name,                    # name of the device
            # port of the pi, from which device is connected
            "port": device.port,
            "location": device.location,            # location of device e.g. kitchen
            "desc": device.desc,                    # description of the device
            # status of the device, wether it is on or off
            "status": device.status,
            "monitoring": device.monitoring,        # wheather device allow monitoring or not
            # if monitoring is on then which measurement it uses if not then null
            "measurement": device.measurement,
            "min_intensity": device.min_intensity,  # min intensity of the device
            "max_intensity": device.max_intensity,  # max intensity of the device
            "cur_intensity": device.cur_intensity   # current intensity of the device
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
    if(validate_token(data)):
        try:
            dev_name = data['device_name']
            operation = data['operation']
            from server import client
            client.publish("cmd/toggle/{}".format(dev_name),
                           operation).wait_for_publish()
            return jsonify({"message": "published"}), 200
        except Exception as e:
            print(str(e))
            return jsonify({"msmessage": str(e)}), 500
    else:
        return jsonify({"message": "Unauthorize"}), 300


@deviceBP.route('/intensity', methods=['POST'])
def change_intensity():
    '''
        1. take input as token and name of device and future intensity.
        2. publish this request as a topic for 'cmds/intensity/device_name'.
        3. return success or failure along with new intensity of device.
    '''
    data = request.json
    if(validate_token(data)):
        try:
            dev_name = data['device_name']
            intensity = data['intensity']
            from server import client
            client.publish("cmd/intensity/{}".format(dev_name),
                           intensity).wait_for_publish()
            return jsonify({"message": "published"}), 200
        except Exception as e:
            print(str(e))
            return jsonify({"msmessage": str(e)}), 500
    else:
        return jsonify({"message": "Unauthorize"}), 300

#######################################################################################
############################ MONITORING ###############################################
#######################################################################################


@deviceBP.route('/getrangedata', methods=['POST'])
def get_range_data():
    '''
        1. Take input as range (min, max, freq), token and device id.
        2. Query InfluxDB for this range data with the measurement as device name.
        3. return this data in json format.
    '''
    data = request.json
    if(validate_token(data)):
        try:
            from server import SQLSession
            session = SQLSession()
            d = session.query(Device).filter_by(id=data['id']).first()
            session.close()
            if not d:
                return jsonify({"message": "No such device"}), 400
            if d.monitoring == False:
                return jsonify({"message": "Monitoring not allowed"}), 404

            from influxdb import InfluxDBClient
            dbname = "ihome"
            host = "influx"
            port = 8086
            influx_client = InfluxDBClient(host=host, port=port)
            influx_client.switch_database(dbname)
            q = 'SELECT * FROM {} WHERE time > now() - {};'.format(d.measurement,
                                                                   data['duration'])
            a = influx_client.query(q)
            return jsonify({
                "data": list(a.get_points(measurement=d.measurement))
            }), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500
    else:
        return jsonify({"message": "Unauthorize"}), 300


@deviceBP.route('/getlatestdata', methods=['POST'])
def get_latest_data():
    '''
        1. Take input as token and device id.
        2. Query InfluxDB for latest entry.
        3. return this data in json format.
    '''
    data = request.json
    print(data)
    if(validate_token(data)):
        try:
            from server import SQLSession
            session = SQLSession()
            d = session.query(Device).filter_by(id=data['id']).first()
            session.close()
            if not d:
                return jsonify({"message": "No such device"}), 400
            if d.monitoring == False:
                return jsonify({"message": "Monitoring not allowed"}), 404

            from influxdb import InfluxDBClient
            dbname = "ihome"
            host = "influx"
            port = 8086
            influx_client = InfluxDBClient(host=host, port=port)
            influx_client.switch_database(dbname)
            q = 'SELECT LAST(value) FROM {}'.format(d.measurement)
            a = influx_client.query(q)
            print(list(a.get_points(measurement=d.measurement)))
            return jsonify({
                "data": list(a.get_points(measurement=d.measurement))
            }), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500
    else:
        return jsonify({"message": "Unauthorize"}), 300


##################################################################################
########################## ADDING IN DEVICE ######################################
##################################################################################

@deviceBP.route('/add', methods=['POST'])
def add_device():
    from server import SQLSession
    session = SQLSession()
    data = request.json
    new_device = Device(
        name=data["name"],
        port=data["port"],
        alias=data["alias"],
        monitoring=data["monitoring"],
        measurement=data["measurement"],
        min_intensity=data["min_intensity"],
        max_intensity=data["max_intensity"],
        cur_intensity=data["cur_intensity"],
        location=data["location"],
        desc=data["desc"],
        created_on=datetime.datetime.utcnow(),
        updated_on=datetime.datetime.utcnow()
    )
    try:
        session.add(new_device)
        session.commit()
        session.close()
        return jsonify({"message": "success"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
