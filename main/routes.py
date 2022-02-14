from main.models import User, Restaurant, Food, Order, Itms
from flask import render_template, url_for, flash, redirect, request
from main.forms import RegistrationForm, UpdateAccountForm, LoginForm
from main import app, db, bcrypt
from datetime import datetime
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
import json
import time

toms = [
        {
            'restaurantname': 'Burger King',
            'price': 570,
            'image': 'burgerking.png',
            'date_created': datetime.utcnow().strftime('%m %d %y - %H:%M:%S'),
            'selecteditems': [
                {
                    'name': 'Margarita Pizza',
                    'price': 250,
                    'image': 'food1.jpeg',
                    'quantity': 1
                },
                {
                    'name': 'Italian Farm Pizza',
                    'price': 320,
                    'image': 'food1.jpeg',
                    'quantity': 1
                }

            ]
        },
        {
            'restaurantname': 'Cheesecake Factory',
            'price': 250,
            'image': 'cheesecakefactory.png',
            'date_created': datetime.utcnow().strftime('%m %d %y - %H:%M:%S'),
            'selecteditems': [
                {
                    'name': 'Margarita Pizza',
                    'price': 250,
                    'quantity': 1
                 }
            ]
        }
]
foods = {
    'restaurantname': 'Burger King',
    'selecteditems': [
        {
            'name': 'Margarita Pizza',
            'price': 250,
            'image': 'food1.jpeg',
            'quantity': 1
        },
        {
            'name': 'Italian Farm Pizza',
            'price': 320,
            'image': 'food1.jpeg',
            'quantity': 1
        }
    ]
}
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/restaurants")
@login_required
def restaurants():
    restaurants_list = Restaurant.query.all()
    return render_template('list_restaurants.html', title='Restaurants', restaurants=restaurants_list)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(url_for(next_page[1:])) if next_page else redirect(url_for('home'))
        else:
            flash('Please check email and password', 'danger')
    return render_template('login.html', form=form, title='Login')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/order/<int:restaurantid>")
def order(restaurantid):
    restaurant = Restaurant.query.get(int(restaurantid))
    restaurants_list = Restaurant.query.all()
    must = {
        'name' : restaurant.name
    }
    return render_template('order.html', title=restaurant.name, restaurants=restaurants_list, name=restaurant.name, foods=restaurant.foods, must=must)

@app.route("/hello", methods=['GET','POST'])
def hello():
    if request.method == 'POST':
        global response
        response = request.get_json()
        return 'OK', 200

@app.route("/cart", methods=['GET', 'POST'])
@login_required
def cart():
    total = 0
    return render_template('cart.html', title='Cart', foods=foods, total=total)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_fn = save_picture(form.picture.data)
            current_user.image_file = picture_fn
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile/'+current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/orders")
def orders():
    items = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('orders.html', title='Orders', tom=items)

@app.route("/checkout", methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        itms = data['itms']
        order = Order(restaurantname=name, active='false', user_id=current_user.id)
        db.session.add(order)
        db.session.commit()
        orders = Order.query.all()
        orderid = orders[len(orders)-1].id
        for i in range(len(itms)):
            items = Itms(name=itms[i]['name'], price=itms[i]['price'], quantity=itms[i]['quantity'], order_id=orderid )
            db.session.add(items)
        db.session.commit()
        return 'OK', 200
    return render_template('checkout.html', title='Checkout')

@app.route("/category/<string:categoryname>")
def category(categoryname):
    lists = Restaurant.query.filter_by(type=categoryname).all()
    return render_template('category.html', title=categoryname, restaurants=lists)