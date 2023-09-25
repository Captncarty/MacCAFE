from flask import jsonify, make_response, flash, redirect, url_for, render_template, abort
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app import app, db, send_email
from app.models.user import User
from flask_login import login_required, current_user
from flask_swagger_ui import get_swaggerui_blueprint
from app.models.gen_user import generate_username, generate_password
import threading
from expired_users import delete_expired_users
import os

#swagger config
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
SWAGGER_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "CAFE API"
    }
)

app.register_blueprint(SWAGGER_BLUEPRINT, url_prefix=SWAGGER_URL)
scheduler = BackgroundScheduler()

def delete_expired_users():
    """ Delete expired users
    """
    with app.app_context():
        expired_users = User.query.filter(User.expires_at < datetime.utcnow()).all()
        for user in expired_users:
            if user.is_admin:
                pass
            db.session.delete(user)
        db.session.commit()

scheduler.add_job(delete_expired_users, 'cron', hour='*', minute=0)  # Schedule the job to run daily at midnight
scheduler.start()


@app.errorhandler(404)
def not_found(error):
    """ 404 Error
    ---
    responses:
      404:
        description: a resource was not found
    """
    return make_response(jsonify({'error': "Not found"}), 404)


@app.errorhandler(403)
def forbidden(error):
    """ 403 Error
    ---
    responses:
      403:
        description: forbidden
    """
    return make_response(jsonify({'error': "Forbidden"}), 403)


@app.errorhandler(405)
def not_allowed(err):
    """ 405 Error
    ---
    response:
        405:
            description: Not Allowed
    """
    return make_response(jsonify({'error': "Not Allowed"}), 405)


@app.errorhandler(401)
def unauthorized(err):
    """ 401 Error
    ---
    response:
        401:
            description: client user can’t be identified
    """
    return make_response(jsonify({'error': "unauthorized"}), 405)


if __name__ == '__main__':
    
    host = '127.0.0.1'
    port = 5001
    app.run(host=host, port=port, debug=True)