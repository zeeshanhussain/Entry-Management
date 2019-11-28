import os
import time
from datetime import datetime

import bcrypt
import pymongo
from bson import ObjectId
from flask import Flask, render_template, flash, redirect, url_for, session
from flask_mail import Mail, Message
from flask_pymongo import PyMongo
from twilio.rest import Client

from forms import RegistrationForm, LoginForm, CheckInForm, CheckOutForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Em'
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
ACCOUNT_SID = os.environ.get('ACCOUNT_SID')
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')
SENDER_USERNAME = os.environ.get('SENDER_USERNAME')
mail = Mail(app)
client = Client(ACCOUNT_SID, AUTH_TOKEN)
mongo = PyMongo(app)


@app.route('/')
@app.route('/home')
def home():
    print(os.environ.get('MAIL_USERNAME'))
    if 'email' in session:
        host = mongo.db.hosts
        host_details = host.find_one({'email': session['email']})
        if host_details is not None:
            visitor = mongo.db.visitor
            host_id = host_details['_id']
            all_visitors = visitor.find({'host_id': str(host_id)}).sort('checkin', pymongo.DESCENDING)
            return render_template('logs.html', visitors=all_visitors)
        return render_template('logs.html')
    return render_template('index.html')


@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    form = CheckInForm()
    host = mongo.db.hosts
    get = (host.find({'available': True}))
    form.host_id.choices = [(str(g['_id']), g['name']) for g in get]
    if get.count() == 0:
        flash('There are no hosts available at the moment.', 'danger')
        return redirect(url_for('home'))
    if form.validate_on_submit():
        visitor = mongo.db.visitor
        visitor_name = form.name.data
        visitor_email = form.email.data
        visitor_number = form.mobile.data
        visitor_checkin = int(time.time()) + 1
        visitor_checkout = 1
        host_id = form.host_id.data
        if host_id is None:
            flash('There are no hosts available at the moment.', 'danger')
            return redirect(url_for('home'))
        visiting = visitor.find_one({'email': visitor_email, 'checkout': 1})
        if visiting is not None:
            flash('Please Checkout Before visiting another host', 'danger')
            return redirect(url_for('home'))

        visitor.insert({'name': visitor_name, 'host_id': host_id, 'email': visitor_email, 'number': visitor_number,
                        'checkin': visitor_checkin, 'checkout': visitor_checkout})
        host.update_one({'_id': ObjectId(host_id)}, {"$set": {'available': False}})
        sms_host(visitor_name, visitor_email, visitor_number, visitor_checkin)
        email_host(visitor_name, visitor_email, visitor_number, visitor_checkin)
        flash('Successfully Checked In', 'success')
        return redirect(url_for('home'))

    return render_template('checkin.html', form=form)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = CheckOutForm()
    if form.validate_on_submit():
        visitor = mongo.db.visitor
        host = mongo.db.hosts
        visitor_email = form.email.data
        visitor_checkout = int(time.time())
        visitor_details = visitor.find_one({'email': visitor_email, 'checkout': 1})
        if visitor_details is None:
            flash('Please Check-In first', 'danger')
            return redirect(url_for('home'))
        host_id = visitor_details['host_id']
        visited = visitor.update_one({'email': visitor_email, 'checkout': 1}, {"$set": {'checkout': visitor_checkout}})
        if visited.matched_count > 0:
            host.update_one({'_id': ObjectId(host_id)}, {"$set": {'available': True}})
            host_details = host.find_one({'_id': ObjectId(host_id)})
            email_visitor(visitor_details['name'], visitor_email, visitor_details['number'], visitor_details['checkin']
                          , visitor_details['checkout'], host_details['name'], host_details['address'])
            flash('Successfully Checked Out', 'success')
            return redirect(url_for('home'))
        flash('Please Check-In first', 'danger')
        return redirect(url_for('home'))

    return render_template('checkout.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'email' in session:
        return redirect('/')
    form = RegistrationForm()
    if form.validate_on_submit():
        host = mongo.db.hosts
        host_name = form.name.data
        host_email = form.email.data
        host_number = form.mobile.data
        host_address = form.address.data
        existing = host.find_one({'email': host_email})
        if existing is None:
            hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
            host.insert(
                {'name': host_name, 'email': host_email, 'password': hashed_password, 'number': host_number, 'address':
                    host_address, 'available': True})
            flash(f'Host Account Created for {form.name.data}!', 'success')
            session['email'] = host_email
            return redirect(url_for('home'))
        flash(f'Account Exists for {form.email.data}!', 'danger')
        return redirect(url_for('register'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if 'email' in session:
        return redirect('/')
    if form.validate_on_submit():
        host = mongo.db.hosts
        host_email = form.email.data
        existing = host.find_one({'email': host_email})
        if existing is None:
            flash('Invalid username/password combination', 'danger')
            return redirect(url_for('login'))
        hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), existing['password'])
        if hashed_password == existing['password']:
            session['email'] = host_email
            return redirect(url_for('home'))
        flash('Invalid username/password combination', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')


@app.template_filter('ctime')
def timectime(s):
    if s == 1:
        return ""
    return datetime.fromtimestamp(s).strftime('%H:%M')


@app.template_filter('datefilter')
def datefilter(s):
    if s == 1:
        return ""
    return datetime.fromtimestamp(s).strftime('%d %b, %Y')


def sms_host(name, email, number, check):
    checkin_time = datetime.fromtimestamp(check).strftime('%H:%M')
    text = f"Dear Host, {name} is coming to visit you, Here are the details \n Name: {name} " \
           f"\n Email: {email} \n " \
           f"Number: {number} \n Check-In Time: {checkin_time}"
    message = client.messages.create(
        to="+91" + number,
        from_=TWILIO_NUMBER,
        body="hello")


def email_host(name, email, number, check):
    checkin_time = datetime.fromtimestamp(check).strftime('%H:%M')
    text = f"Dear Host, {name} is coming to visit you, Here are the details \n 'Name: {name} " \
           f"\n Email: {email} \n " \
           f"Number: {number} \n Check-In Time: {checkin_time}"
    msg = Message('New Visitor',
                  sender=SENDER_USERNAME,
                  recipients=[email])
    msg.body = text
    mail.send(msg)


def email_visitor(name, email, number, check_in, check_out, host_name, address):
    checkin_time = datetime.fromtimestamp(check_in).strftime('%H:%M')
    checkout_time = datetime.fromtimestamp(check_out).strftime('%H:%M')
    text = f"Dear {name}, Here are the details \n Name: {name} " \
           f"\n Email: {email} \n " \
           f"Number: {number} \n Check-In Time: {checkin_time}" \
           f"\n Check-out Time: {checkout_time} \n Host Visited:{host_name} " \
           f"\n Address Visited: {address}"
    msg = Message('Details of Visit',
                  sender=SENDER_USERNAME,
                  recipients=[email])
    msg.body = text
    mail.send(msg)


if __name__ == "__main__":
    app.debug = True
    app.run()
