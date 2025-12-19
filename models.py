from database import db
from datetime import datetime

# ---database models---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    img = db.Column(db.String(10)) 
    category = db.Column(db.String(20))
    stock = db.Column(db.Integer, default=0)

class Promo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    discount_percent = db.Column(db.Integer, nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    subtotal = db.Column(db.Integer)
    promo_info = db.Column(db.String(100))
    total = db.Column(db.Integer)
    amount_paid = db.Column(db.Integer)
    change = db.Column(db.Integer)
    cashier_name = db.Column(db.String(50))