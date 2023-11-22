from flask import request, redirect, url_for, jsonify, abort
import jwt
from os import environ
import datetime

from . import api
from app import db
from app.models import Data

import requests

# RECEIVE THE DATA FROM THE NODEMCU, PROCESS IT BEFORE SAVING INTO DATABASE
@api.route('/get_water_temp', methods=["POST"])
def get_water_temp():
    authorization_key = request.headers.get('Authorization')

    if authorization_key == environ.get('SECRET_KEY'):

        # Get the current timestamp
        current_time = datetime.datetime.utcnow()

        # Check if it's been at least 15 minutes since the last data entry
        last_entry = Data.query.order_by(Data.datetime.desc()).first()
        
        if last_entry is None or (current_time - last_entry.datetime).total_seconds() >= 120:
            # Accept data
            received_data = request.get_json()
            data = Data(water_temp_value=received_data["temperature"], main_container_status=received_data["main_container"], backup_container_status=received_data["backup_container"], datetime= datetime.datetime.utcnow())

            db.session.add(data)
            db.session.commit()

            return received_data
        
    else:
        abort(403)

    return {}

# GET THE DATA FROM DATABASE AND FETCH IT
@api.route('/retrieve_water_temp', methods=["GET"])
def retrieve_water_temp():
    
    last_data = Data.query.order_by(Data.id.desc()).first()

    if last_data is not None:
        current_datetime = last_data.datetime.strftime("%a %B %d %Y %X")

        return jsonify(
            {
                'temp': last_data.water_temp_value,
                'current_datetime' : current_datetime,
                'main_container_status' : last_data.main_container_status,
                'backup_container_status' : last_data.backup_container_status
            }
            )    
    else:
        return jsonify(
            {
                'temp': "NO DATA",
                'current_datetime' : "NO DATA",
                'main_container_status' : "NO DATA",
                'backup_container_status' : "NO DATA"
            }
            )   