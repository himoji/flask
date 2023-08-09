from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, timedelta


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(200))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer = db.Column(db.String(3))
    bounty = db.Column(db.Integer, default = 100)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow() + timedelta(hours=6))
    user_id = db.Column(db.Integer)
    taker_id = db.Column(db.Integer, default = 0)
    user_name = db.Column(db.String(16))
    taker_name = db.Column(db.String(16), default='')
    money = db.Column(db.Integer, default = 0)
    ttype = db.Column(db.String(20))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    money = db.Column(db.Integer, default=0)
    answered = db.Column(db.String(300))
    notes = db.relationship('Note')

    # TODO: stocks, fees
