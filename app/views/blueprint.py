import logging
import requests
from os import environ as env
import requests
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, abort, session
from flask_login import login_user, current_user, login_required, logout_user
from flask_login import LoginManager
from app.models.gen_user import generate_username, generate_password
from app.models.user import User
from app import db, app, send_email, send_email_subscribe, get_paystack_transaction
from datetime import datetime, timedelta


secret_key = env.get('PAYSTACK_SECRET_KEY')
public_key = env.get('PAYSTACK_PUBLIC_KEY')

"""
log user
"""

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


login_manager = LoginManager(app)
login_manager.login_view = "my_blueprint.login"
@login_manager.user_loader

def load_user(user_id):
    """Args:
        user_id int
    Returns:
        user object from your database based on user_id
    """
    return User.query.get(int(user_id))

# def delete_expired_users():
#     """ delete users that have hit the expiration time """
#     try:
#         expiration_time = datetime.utcnow()
#         expired_users = User.query.filter(User.created_at < expiration_time).all()

#         with app.app_context():
#             with db.session.begin():
#                 for user in expired_users:
#                     db.session.delete(user)
                
#                 # Commit the transaction after deleting all users
#                 db.session.commit()
#                 app.logger.info('Expired users deleted successfully')

#     except Exception as e:
#         app.logger.error(f'An error occurred while deleting expired users: {e}')

#     scheduler.add_job(delete_expired_users, 'interval', hours=24)


my_blueprint = Blueprint('my_blueprint', __name__)

@my_blueprint.route('/')
def index():
    """ returns landing page or dashboard if user is logged in
    """
    if current_user.is_authenticated:
        return redirect(url_for('my_blueprint.dashboard'))
    return render_template('landing.html', paystack_public_key=public_key)


@my_blueprint.route('/redirect_url', methods=['GET', 'POST'])
def redirect_url():
    """ redirect user to the internet upon successful login"""
    return redirect("http://www.google.com")


@my_blueprint.route('/stats', strict_slashes=False)
def stats():
    """ test route
    """
    return jsonify('working alright') 


@app.route('/verify_transaction', methods=['POST'])
def verify_transaction():
    """ verify transaction from paystack
    upon successful verification, create user and send email
    """
    data = request.get_json()
    reference = data.get('reference')
    email = data.get('email')
    package = data.get('package')
    duration = data.get('duration')
    price = data.get('price')
    # user = User.query.get(reference)

    # if user.reference == reference:
    #     abort(401)
    #     app.logger.info(f'Reference no: {reference}, Already verified!')
    # Call the get_paystack_transaction function
    # Retrieve data from session storage
    # package = request.cookies.get('selectedPackage')
    # duration = request.cookies.get('selectedDuration')
    # price = request.cookies.get('selectedPrice')
    result = get_paystack_transaction(reference, secret_key)
    app.logger.info(f'Verifying transaction with reference: {reference}')

    if result is not None:
        # Transaction was successfully verified
        
        username = generate_username()
        password = generate_password()

        user = User(username=username, password=password, reference=reference, package=package, duration=duration, price=price, is_admin=False)
        db.session.add(user)
        db.session.commit()
        send_email(email, username, password, duration, package)
        app.logger.info(f'Transaction verified! User ID: {user.id} Username: {username} Package: {package} Duration: {duration}')
        return jsonify({'result': True})
    else:
        # Transaction verification failed
        return jsonify({'result': False})


@my_blueprint.route('/create_user', methods=['GET', 'POST'])
def create_user():
    """ Create a new user and send email,
    initial setup
    """
    if request.method == 'POST':
        email = request.form.get('email')
    
        username = generate_username()
        password = generate_password()
        reference = 830031789

        user = User(username=username, password=password, reference=reference, is_admin=False)
        db.session.add(user)
        db.session.commit()
        
        send_email(email, username, password)

        flash('User created successfully. Check your email for credentials.', 'success')
        return redirect(url_for('my_blueprint.login'))
        
        #return f'New User Created<br>Username: {username}<br>Password: {password}'
    #return render_template('create_user.html')
    return redirect(url_for('my_blueprint.index'))


@my_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """ login method
    checks if user has expired,
    if valid login in user else delete user from database
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        
        if user.expires_at < datetime.utcnow():
            if user.is_admin:
                pass
            else:
                app.logger.info(f'{username} has expired and deleted from the database')
                db.session.delete(user)
                db.session.commit()
            
                flash(f'{username} has expired')
                return redirect(url_for('my_blueprint.index'))
        
        if user and user.password == password:
            login_user(user)
            if current_user.is_admin:
                app.logger.info('logged in Admin')
                return redirect(url_for('admin_dashboard'))
            else:
                logging.info('User logged in: {username}'.format(username=username))
                
                return redirect(url_for('my_blueprint.redirect_url'))
        elif user:
            logging.info('Invalid password: {username}'.format(username=username))
            flash('Invalid password', 'try again')
            return redirect(url_for('my_blueprint.index'))
        else:
            flash('Login failed. Check credentials', 'try again')
    return redirect(url_for('my_blueprint.index'))


@my_blueprint.route('/logout')
def logout():
    """ Logout method
    if from an active user, end session and redirect
    back to landing page
    """
    if current_user:
        logging.info('User logged out: %s', current_user.username)
        logout_user()
        flash('Logout successful', 'success')
        return redirect(url_for('my_blueprint.index'))
    flash("You're not logged in", 'fail')
    return render_template("landing.html")


# @my_blueprint.route('/logout_inactive')
# @login_required
# def logout_inactive():
#     # Check if the user has been inactive for a specified period (e.g., 30 minutes)
#     inactivity_threshold = timedelta(seconds=30)
#     if datetime.utcnow() - current_user.last_activity >= inactivity_threshold:
#         logout_user()
#         flash('You have been logged out due to inactivity.', 'info')
#         return redirect(url_for('my_blueprint.login'))

#     return redirect(url_for('my_blueprint.dashboard'))


# @my_blueprint.route('/api/active_users', methods=['GET'])
# @login_required
# def view_active_users():
#     if current_user.is_admin:  # Check if the user is an admin (customize this condition)
#         # Define an inactivity threshold (e.g., 30 minutes)
#         inactivity_threshold = timedelta(minutes=30)
#         active_users = [user for user in User.query.all() if (datetime.utcnow() - user.last_activity) <= inactivity_threshold]
#         active_user_list = [{'id': user.id, 'username': user.username} for user in active_users]
#         return jsonify(active_users=active_user_list)
#     else:
#         return jsonify(message='Permission denied'), 403


@my_blueprint.route('/dashboard')
@login_required
def dashboard():
    """ User access page after authentication
    """
    if current_user.is_admin:
        user = current_user.username
        return render_template("admin_dashboard.html", user=user)
    else:
        user = current_user.username
        return render_template("welcome.html", user=user)


@my_blueprint.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """ an api access to delete users by admin
    """
    if current_user.is_admin:
        user = User.query.get(user_id)
        if not user:
            abort(404)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
        return redirect(url_for('my_blueprint.logout'))
    return abort(403)

# @my_blueprint.route('/api/users', methods=['GET'])
# def view_users():
#     #if current_user.is_admin:
#     users = User.query.all()
#     if users:
#         user_list = [{'id': user.id, 'username': user.username} for user in users]
#         return jsonify(users=user_list)
#     return jsonify({'message': 'You are not authorized to perform that function.'}), 403


@my_blueprint.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    """if form is filled correctly,
    retrieve mail and send notification
    """
    if request.method == 'POST':
        email = request.form.get('email')
        
        send_email_subscribe(email)

        flash('Thank you for subscribing!', 'success')
        app.logger.info('New subscriber: {email}'.format(email=email))
        return redirect(url_for('my_blueprint.index'))
    return render_template('blog.html')
