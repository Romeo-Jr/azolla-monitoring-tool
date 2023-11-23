from . import auth
from flask import render_template, redirect, request, url_for, session, make_response, flash
from app import bcrypt
from app.models import Admin, Log
import jwt
from os import environ
from flask_mail import Message
from app import mail, db

from sqlalchemy.exc import OperationalError

import datetime

# LOGIN PAGE
@auth.route('/login', methods=["POST", "GET"])
def login():

    token = request.cookies.get('token')

    if token:
        return redirect(url_for('main.dashboard'))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            user = Admin.query.filter_by(email = email).first()
        except OperationalError:
            return "<center><h1>Database not Found</h1></center>"

        if user is not None:
            if email == user.email:
                checked_password = bcrypt.check_password_hash(user.password, password)

                if checked_password:
                    current_time = datetime.datetime.utcnow()
                    user_logs = Log(user_id=user.id, user_logged_in=current_time, user_logout=current_time)
                    db.session.add(user_logs)
                    db.session.commit()

                    # ENCODE USING JWT
                    encoded_jwt = jwt.encode({'id': user.id}, environ.get("SECRET_KEY"), algorithm="HS256")

                    # STORE IN COOKIES
                    response = make_response(redirect('dashboard'))
                    response.set_cookie('token', encoded_jwt)

                    return response
                
                else:
                    flash("Incorrect Email or Password")
                    return redirect("login")
        else:
            flash("User doesn't exist")
            
    return render_template('login.html')

# PASSWORD RESET
@auth.route('/reset_password', methods=["POST", "GET"])
def reset_password():

    if request.method == "POST":
        user = Admin.query.filter_by(email = request.form["email"]).first()

        if user is None:
            flash("Email is not registered", "error")
            return redirect(url_for('auth.reset_password'))

        encode_token = jwt.encode({"email": user.email}, environ.get("SECRET_KEY"), algorithm="HS256")
        reset_link = url_for('auth.reset_password_token', token = encode_token, _external=True)
        dev_email = "romeoestoy0101@gmail.com", 
        email = user.email

        msg = Message(subject="Password Reset Request", recipients=[user.email])

        msg.html = f"""<h3>Dear Mam/Sir,</h3>
                    <p>We received a request to recover your account associated with the email address: { email }. If this was not initiated by you, please disregard this email.</p>
                    <p>To reset your account password, please click on the link below:</p>
                    <p><a href='{ reset_link }'>{ reset_link }</a></p>
                    <p>If you are unable to click the link, please copy and paste it into your browser's address bar.</p>
                    <p>If you did not request this password reset, please contact our support team immediately at { dev_email } for assistance.</p>
                    <br>
                    <p>Thank you for using our services.</p>"""

        mail.send(msg)
        flash('Password reset instructions sent to your email.', "success")

    return render_template('forgot_password.html')

# RESET PASSWORD PAGE
@auth.route('/reset_password/<token>', methods=["POST", "GET"])
def reset_password_token(token):
    try:
        decode_token = jwt.decode(token, environ.get("SECRET_KEY"), algorithms="HS256")
        email = decode_token["email"]

        user = Admin.query.filter_by(email = email).first()

        if request.method == "POST":
            user_pass = request.form["password"]
            user.password = bcrypt.generate_password_hash(user_pass)
            db.session.commit()

            flash("Password updated", "success")
            return redirect(url_for('auth.login'))

        return render_template('update_password.html')
    
    except:
        return redirect(url_for('auth.login'))

