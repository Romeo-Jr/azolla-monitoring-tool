from app import db

# DATABASE TABLE
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db .String(255), nullable=False)
    profile_pic = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    water_temp_value = db.Column(db.Float, nullable=False)
    main_container_status = db.Column(db.Integer, nullable=False)
    backup_container_status = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    user_logged_in = db.Column(db.DateTime, nullable=False)
    user_logout = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=True)
    