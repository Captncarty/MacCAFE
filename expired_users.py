from app import app, db
from app.models.user import User
import threading
from datetime import datetime, timedelta


def delete_expired_users():
    while True:
        # expiration_time = datetime.utcnow() - timedelta(hours=24)
        with app.app_context():
            expired_users = User.query.filter(User.created_at < User.expires_at).all()
            
            with db.session.begin():
                for user in expired_users:
                    db.session.delete(user)
        
            db.session.commit()
            app.logger.info('Expired users deleted successfully')
        
        # Sleep for 24 hours before checking again
        threading.Event().wait(24 * 3600)