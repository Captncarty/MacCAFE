from os import environ as env
from flask import Flask, session
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
import threading
import time




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///User.db'  # Change this to your database URI
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


def send_email(email, username, password, duration, package):
    msg = Message('Your Credentials', sender='your_email@gmail.com', recipients=[email])
    msg.body = f'Username: {username}\nPassword: {password}\nDuration: {duration}hour\nPackage: {package}'
    mail.send(msg)

def send_email_subscribe(email):
    msg = Message("Welcome to MacCAFE", sender='your_email@gmail.com', recipients=[email])
    msg.body = f'Stay Tuned to the best deals and latest updates. Great to have you here \U0001F601!'
    mail.send(msg)

def get_paystack_transaction(reference, secret_key):
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

from app.views.blueprint import my_blueprint
from app.views.view import my_views


session_activity = {}

# Periodically check session activity and log out inactive users
def check_session_activity():
    while True:
        for session_id, last_activity_time in session_activity.copy().items():
            if time.time() - last_activity_time > 3600:  # Inactivity period (e.g., 1 hour)
                # Mark the user as logged out (you can implement your own logic)
                session_activity.pop(session_id)
        time.sleep(1800)  # Check every 30 minutes

# A route to simulate user activity (update session activity)
@app.route('/simulate_activity')
def simulate_activity():
    session_activity[session.get('id')] = time.time()
    return 'Activity recorded'


app.register_blueprint(my_blueprint)
app.register_blueprint(my_views)
# Start the session activity checker as a background thread
session_checker_thread = threading.Thread(target=check_session_activity)
session_checker_thread.daemon = True
session_checker_thread.start()

# Additional configuration options (optional)
# app.config['DEBUG'] = True  # Enable debug mode (for development)
# app.config['SQLALCHEMY_ECHO'] = True  # Print SQL statements (for debugging)

