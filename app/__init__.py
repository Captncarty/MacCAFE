from os import environ as env
import smtplib
from flask import Flask, session, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from threading import Thread
import time




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///User.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.secret_key = 'turtle'



""" mail service setup
"""
user_mail = env.get('USER_EMAIL')
mail_password = env.get('USER_PASSWORD')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
#app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = user_mail
app.config['MAIL_PASSWORD'] = mail_password
app.config['MAIL_DEFAULT_SENDER'] = user_mail

mail = Mail(app)


""" store session activity in dict and inactivity period
"""
session_activity = {}

INACTIVITY_PERIOD = 1800





def send_email(email, username, password, duration, package):
    """ send email to login details and info toverified subscriber
    """
    msg = Message('Your Credentials', sender='your_email@gmail.com', recipients=[email])
    msg.body = f'Username: {username}\nPassword: {password}\nDuration: {duration}hour\nPackage: {package}'
    mail.send(msg)

def send_email_subscribe(email):
    """ send email to verified subscriber
    """
    try:
        msg = Message("Welcome to MacCAFE", sender='your_email@gmail.com', recipients=[email])
        msg.body = f'Stay Tuned to the best deals and latest updates. Great to have you here \U0001F601!'
        mail.send(msg)
    except smtplib.SMTPException as e:
            return jsonify(f"Error: {e}", "check network")

def get_paystack_transaction(reference, secret_key):
    """ verify paystack transaction
    Args:
        reference no
        secret_key from paystack API

    Returns:
        A status code of 200 if transaction is successful
    """
    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Cache-Control": "no-cache",
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()  # Parse the JSON response
        else:
            return None  # Return None for invalid responses
    except requests.exceptions.RequestException as e:
        return None  # Return None for request exceptions

 
def check_session_activity():
    """ Periodically check session activity and log out inactive users
    Inactivity period (e.g., 1 hour)
    Mark the user as logged out
    """
    while True:
        current_time = time.time()
        sessions_to_remove = [session_id for session_id, last_activity_time in session_activity.items() if current_time - last_activity_time > INACTIVITY_PERIOD]
        for session_id in sessions_to_remove:
            session_activity.pop(session_id)
        time.sleep(900)

@app.route('/simulate_activity')
def simulate_activity():
    """Simulate user activity and record it."""
    session_id = session.get('id')
    if session_id:
        session_activity[session_id] = time.time()
        return 'Activity recorded'
    else:
        return 'Session ID not found'

""" importing blueprints and registering application routes
"""
from app.views.blueprint import my_blueprint
from app.views.view import my_views
app.register_blueprint(my_blueprint)
app.register_blueprint(my_views)


""" Start the session activity checker as a background thread
"""
session_checker_thread = Thread(target=check_session_activity)
session_checker_thread.daemon = True
session_checker_thread.start()

"""
Additional configuration options (optional)
app.config['DEBUG'] = True  # Enable debug mode (for development)
app.config['SQLALCHEMY_ECHO'] = True  # Print SQL statements (for debugging)
"""

