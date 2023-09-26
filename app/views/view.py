"""
setting up api calls and routes for the app
"""
import requests
import random
from os import environ as env
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, abort
from flask_login import login_user, current_user, login_required, logout_user
from flask_login import LoginManager
from app.models.gen_user import generate_username, generate_password
from app.models.user import User
from app import db, app, send_email, get_paystack_transaction
from datetime import datetime, timedelta

# login_manager = LoginManager(app)
# login_manager.login_view = "my_blueprint.login"
# @login_manager.user_loader

secret_key = env.get('PAYSTACK_SECRET_KEY')

my_views = Blueprint('view', __name__)

@app.route('/st')
def run():
    return jsonify('worked')


@app.route('/api/users', methods=['GET'])
@login_required
def view_users():
    """ view registered users stored in database
    """
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    if users:
        user_list = [{
            'id': user.id,
            'username': user.username,
            'password': user.password,
            'created_at': user.created_at,
            'expires_at': user.expires_at,
            'reference': user.reference,
            'price': user.price,
            'speed': user.speed,
            'package': user.package,
            'duration': user.duration
        } for user in users]
        return jsonify(users=user_list)
    return jsonify({'message': 'You are not authorized to perform that function.'}), 403


@app.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
def users_by_id(user_id):
    """ Search for user with given id
    """
    if not current_user.is_admin:
        abort(403)
    user = User.query.get(user_id)
    if user:
        return jsonify({'id': user.id, 'username': user.username, 'password': user.password, 'reference': user.reference})
    return jsonify({'message': 'User not available.'}), 403


@app.route('/api/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    """ Create new user as an Admin
    """
    if current_user.is_admin:
        username = generate_username()
        password = generate_password()
        reference = random.randint(100000000, 999999999)
        package = "Lite"
        duration = "2"
        price = "5"


        if username and password:
            user = User(username=username, password=password, reference=reference, price=price, package=package, duration=duration, is_admin=False)
            db.session.add(user)
            db.session.commit()
            app.logger.info(f'New User: user_id: {user.id} username: {user.username} reference no: {user.reference}, package: {user.package}, duration: {user.duration}')
            return jsonify({'id': user.id, 'username': user.username, 'password': user.password, 'reference': user.reference, 'package': user.package, 'duration': user.duration})
        return jsonify({'message': 'check details'}), 403
    return abort(401)


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    """ Admin specified dashboard
    """
    if current_user.is_admin:
        # Only allow admin users to access the admin dashboard
        return render_template('admin_dashboard.html')
    else:
        return 'Permission denied', 403

@app.route('/user/<int:user_id>/delete', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """ Delete user with given id
    """
    if not current_user.is_admin:
        abort(403)  # Forbidden for non-admin users
    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        return jsonify({'message': 'User not found'}), 404
    db.session.delete(user_to_delete)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})



@app.route('/api/user/search', methods=['GET', 'POST'])
@login_required
def search():
    """search for user with their username via html form
    """
    if request.method == 'POST':
        if not current_user.is_admin:
            abort(403)
        username = request.form.get('username')

        user_details = User.query.filter_by(username=username).first()
        if user_details:
            return render_template('admin_dashboard.html', user_details=user_details.username)
        flash('User not found', 'failed')
    return redirect(url_for('admin_dashboard'))


@app.route('/api/search/<string:username>', methods=['GET'])
@login_required
def users_by(username):
    """search for user with their username
    """
    if not current_user.is_admin:
        abort(403)
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template('admin_dashboard.html', user_details=user)
    return jsonify({'message': 'User not available.'}), 403

@app.route('/transactions/<string:reference>', methods=['GET'])
@login_required
def get_transaction_by_reference(reference):
    """ search and verify transaction by reference no
    """
    if not current_user.is_admin:
        abort(403)
    # Verify the transaction using the verify_transaction function
    secret_key = env.get('PAYSTACK_SECRET_KEY')
    verify_url = f'https://api.paystack.co/transaction/verify/{reference}'
    headers = {
        'Authorization': f'Bearer {secret_key}',
        'Cache-Control': 'no-cache',
    }

    response = requests.get(verify_url, headers=headers)

    if response.status_code == 200:
        transaction_data = response.json()
        # Process the transaction data as needed
        return jsonify(transaction_data)
    else:
        return jsonify({'error': 'Transaction verification failed'}), 400
    

@app.route('/transactions', methods=['GET'])
@login_required
def get_all_transactions():
    """ Search for all transactions on paystack
    """
    if not current_user.is_admin:
        abort(403)
    secret_key = env.get('PAYSTACK_SECRET_KEY')
    url = "https://api.paystack.co/transaction"

    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Cache-Control": "no-cache",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        transaction_data = response.json()
        # Process the transaction data as needed
        return jsonify(transaction_data)
    else:
        return jsonify({'error': 'Transaction verification failed'}), 400\
            
@app.route('/blog')
def blog_page():
    """ blog page
    """
    return render_template('blog.html')

@app.route('/api/verify', methods=['POST'])
def verify():
    """ Admin dashboard transaction verification mtd"""
    if not current_user.is_admin:
        abort(403)
    data = request.get_json()
    reference = data.get('reference')
    
    result = get_paystack_transaction(reference, secret_key)
    app.logger.info(f'Verifying transaction with reference: {reference}')

    if result is not None:
        app.logger.info(f'Transaction verified!')
        return jsonify({'result': True})
    else:
        # Transaction verification failed
        return jsonify({'result': False})