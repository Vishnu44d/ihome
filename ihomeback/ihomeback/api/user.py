from flask import request, Blueprint, jsonify
from ihomeback.models.userModel import User
import uuid
import datetime
import json
from ihomeback.auth.auth import validate_token, get_token

userBP = Blueprint('userApi', __name__)

@userBP.route('/register', methods=['GET', 'POST'])
def useraction():
    if request.method == 'POST':
        data = request.json
        return save_new_user(data=data)  
    else:
        response_object = {
            'status': 'fail',
            'message': 'method not allowed',
        }
        return jsonify(response_object), 400


@userBP.route('/login', methods=['GET', 'POST'])
def userLogin():
    if request.method == 'POST':
        data = request.json
        return get_token(data)
    else:
        response_object = {
            'status': 'fail',
            'message': 'method not allowed',
        }
        return jsonify(response_object), 400



def save_new_user(data, isAdmin=False):
    from server import SQLSession
    session = SQLSession()
    user = session.query(User).filter_by(email=data['email']).first()
    if not user:
        new_user = User(
            public_id=str(uuid.uuid4()),
            email=data['email'],
            username=data['username'],
            password=data['password'],
            registered_on=datetime.datetime.utcnow(),
            admin=isAdmin,
        )
        try:
            session.add(new_user)
            session.commit()
            session.close()
            response_object = {
                'status': 'Ok',
                'message': 'User Created Successful',
            }
            return jsonify(response_object), 200
        except Exception as e:
            session.close()
            response_object = {
                'status': 'fail',
                'message': 'Problem saving in db',
                'error': str(e)
            }
            return jsonify(response_object), 500
    else:
        session.close()
        response_object = {
            'status': 'fail',
            'message': 'User already exists. Please Log in.',
        }
        return jsonify(response_object), 400



@userBP.route('/alluser', methods=['GET', 'POST'])
def get_all_users():
    if request.method == 'POST':
        data = request.json
        if validate_token(data):
            from server import SQLSession
            session = SQLSession()
            users_ = session.query(User).all()
            users_ = [{"name": i.username, 
                "email":i.email,
                } for i in users_]
            if len(users_) == 0:
                response_object = {
                    'status': 'success',
                    'message': 'No user yet' 
                }
            else:
                response_object = {
                    'status': 'success',
                    'message': 'giving all users. use it wisely',
                    'payload': users_
                }
            return jsonify(response_object), 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'not a admin'
            }
            return jsonify(response_object), 300
    else:
        response_object = {
            'status': 'fail',
            'message': 'method not allowed'
        }
        return jsonify(response_object), 400
