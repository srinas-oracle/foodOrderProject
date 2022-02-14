from datetime import datetime
from main import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), default='default.jpg', nullable=False)
    password = db.Column(db.String(60), nullable=False)
    orders = db.relationship('Order', backref='author', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurantname = db.Column(db.String(20), nullable=False)
    active = db.Column(db.String(5), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    itms = db.relationship('Itms', backref='owns', lazy=True)

class Itms(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(30), nullable=False, default='default.jpg')
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    location = db.Column(db.String(20), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(15), nullable=False)
    image = db.Column(db.String(30), nullable=False, default='default.jpg')
    foods = db.relationship('Food', backref='provider', lazy=True)
