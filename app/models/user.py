from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta

class User(db.Model, UserMixin):
    """ User model for the flask app
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    reference = db.Column(db.Integer, unique=True, nullable=False)
    package = db.Column(db.String, nullable=False)
    duration = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    speed = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


    def __init__(self, username, password, reference, package, duration, price, is_admin):
        """ Constructor for the User model
        """
        self.username = username
        self.password = password
        self.created_at = datetime.utcnow()
        #  self.expires_at = datetime.utcnow() + timedelta(days=1)
        self.expires_at = self.calculate_expiration(duration)
        self.reference = reference
        self.package = package
        self.duration = duration + " hours"
        self.price = price + " Naira"
        self.speed = self.calculate_speed(package)
        self.is_admin = is_admin

    def calculate_expiration(self, duration):
        """ Calculate the expiration date based on the duration
        """
        data_duration = int(duration)
        if data_duration == 1:
            return self.created_at + timedelta(days=1)
        elif data_duration == 2:
            return self.created_at + timedelta(days=1)
        elif data_duration == 5:
            return self.created_at + timedelta(days=2)
        elif data_duration == 8:
            return self.created_at + timedelta(days=3)
        elif data_duration == 12:
            return self.created_at + timedelta(days=3)
        else:
            return self.created_at + timedelta(days=7)
    
    def calculate_speed(self, package):
        """ Calculates the speed based on the package
        """
        package_speed = package
        if package_speed == "Lite":
            return f'80mbps'
        elif package_speed == "Fast":
            return f'150mbps'
        else:
            return f'300mbps'