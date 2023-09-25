from app import app, db
from app.models.user import User
from datetime import datetime, timedelta

def create_admin_user():
    with app.app_context():
    # Create an admin user
        admin_user = User(
            username='admin',
            password='access',
            reference=700000001,
            package="Cheetah",
            duration="24",
            price="210",
            is_admin=True
        )
    
    # Add the user to the database session and commit the changes
        db.session.add(admin_user)
        db.session.commit()

    
if __name__ == '__main__':
    create_admin_user()