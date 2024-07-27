from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class GasReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, server_default=func.now())

class CurrentReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, server_default=func.now())

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    

    