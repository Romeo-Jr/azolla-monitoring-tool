from . import main
from flask import send_file, render_template, redirect, session, request, url_for, session, make_response, flash, abort
from app import bcrypt
from app.models import Admin, Data, Log
import jwt
from os import environ
from flask_mail import Message
from app import mail, db
import datetime
from sqlalchemy import desc
import pandas as pd
from io import BytesIO
from app import bcrypt

from functools import wraps

def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        access_token = request.cookies.get('token')

        if not access_token:
            abort(404)
        
        try:
            decoded_token = jwt.decode(access_token, environ.get("SECRET_KEY"), algorithms="HS256")
            return view_func(*args, **kwargs)
        
        except Exception as e:
            return e   

    return wrapped_view
    
# DASHBOARD PAGE
@main.route('/dashboard')
@login_required
def dashboard():
    # Get today's date
    today = datetime.datetime.utcnow()
    current_date = today.strftime("%Y-%m-%d")
    all_sensor_data = Data.query.all()

    filtered_data = [row for row in all_sensor_data if row.datetime.strftime("%Y-%m-%d") == current_date]

    return render_template('dashboard.html', sensor_data=filtered_data)

@main.route('/filtered_data', methods=["POST"])
def export_filtered_data():
    
    date_str = request.form["date"]
    date_as_datetime = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    date_as_date = date_as_datetime.date()

    format_date = datetime.datetime.strftime(date_as_date, "%Y-%m-%d")
    
    all_data = Data.query.all()

    filtered_items = {
        "id" : [],
        "water_temp_value" : [],
        "main_container_status" : [],
        "backup_container_status" : [],
        "datetime" : []
    }

    filtered_items["id"] = [log.id for log in all_data if format_date == log.datetime.strftime("%Y-%m-%d")]
    filtered_items["water_temp_value"] = [log.water_temp_value for log in all_data if format_date == log.datetime.strftime("%Y-%m-%d")]
    filtered_items["main_container_status"] = [log.main_container_status for log in all_data if format_date == log.datetime.strftime("%Y-%m-%d")]
    filtered_items["backup_container_status"] = [log.backup_container_status for log in all_data if format_date == log.datetime.strftime("%Y-%m-%d")]
    filtered_items["datetime"] = [log.datetime for log in all_data if format_date == log.datetime.strftime("%Y-%m-%d")]

    df = pd.DataFrame(filtered_items)

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Filtered Data')

    output.seek(0)

    # Send the file in the response
    return send_file(output, download_name=f"{date_as_date}_data.xlsx", as_attachment=True)

# SETTING PAGE
@main.route('/setting')
@login_required
def setting():
    token = request.cookies.get('token')
    user_cookie = jwt.decode(token, environ.get("SECRET_KEY"), algorithms=["HS256"])

    user = Admin.query.filter_by(id = user_cookie['id']).first()
    current_user_logs = Log.query.filter_by(user_id = user.id).order_by(desc(Log.id))

    return render_template('setting.html', user_info=user, current_user_logs=current_user_logs)

# LOGOUT THE USER
# CLEAR THE COOKIES
@main.route('/logout')
@login_required
def logout():
    token = request.cookies.get('token')
    user_cookie = jwt.decode(token, environ.get("SECRET_KEY"), algorithms=["HS256"])

    current_time = datetime.datetime.utcnow()
    user_current_logs = Log.query.filter_by(user_id = user_cookie["id"]).order_by(desc(Log.id)).first()
    
    diff = current_time - user_current_logs.user_logged_in

    duration_in_minutes = diff.seconds / 60
    
    user_current_logs.user_logout = current_time
    user_current_logs.duration = duration_in_minutes

    db.session.commit()

    response = make_response(redirect(url_for('auth.login')))
    response.set_cookie('token', '', expires=0)
    return response

@main.route('/update_profile', methods=["POST", "GET"])
def update_profile():
    if request.method =="POST":
        
        data = request.form
        user_id, user_email, user_password, user_username = data.get("id"), data.get("email"), data.get("password"), data.get("username")

        admin_info = Admin.query.filter_by(id = user_id).first()
        admin_info.id = user_id
        admin_info.email = user_email
        admin_info.username = user_username
        
        if user_password != "":
            admin_info.password = bcrypt.generate_password_hash(user_password)

        db.session.commit()

        flash("Profile updated", "success")
        return redirect(url_for('main.update_profile'))

    token = request.cookies.get('token')
    user_cookie = jwt.decode(token, environ.get("SECRET_KEY"), algorithms=["HS256"])
    
    user = Admin.query.filter_by(id=user_cookie['id']).first()

    return render_template('update_profile.html', user_info = user)

@main.route('/')
def index():
    return render_template('index.html')