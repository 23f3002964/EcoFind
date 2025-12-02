from flask import current_app as app
from flask_security import Security, hash_password
from backend.models import *
from datetime import datetime

# Only run this code if we're in an application context
if app:
    with app.app_context():
        # Create all tables first
        try:
            db.create_all()
        except Exception as e:
            print(f"An error occurred while creating tables: {e}")

        # Create roles
        try:
            with db.session.begin():
                app.security.datastore.find_or_create_role(
                    name='Admin',
                    description='Manages users, subjects, chapters, and quizzes with full control.'
                )
                app.security.datastore.find_or_create_role(
                    name='User',
                    description='Registers, logs in, and attempts quizzes on chosen subjects.'
                )
        except Exception as e:
            print(f"An error occurred while creating roles: {e}")

        # Create users with roles
        try:
            with db.session.begin():
                if not app.security.datastore.find_user(email='bytescode0115@gmail.com'):
                    app.security.datastore.create_user(
                        email='bytescode0115@gmail.com',
                        password=hash_password("12345"),
                        username='bytes_code',
                        roles=['Admin']
                    )

                if not app.security.datastore.find_user(email='hanzalatafzeel44@gmail.com'):
                    app.security.datastore.create_user(
                        email='hanzalatafzeel44@gmail.com',
                        password=hash_password("12345"),
                        username='hanzala@123',
                        roles=['User']
                    )

                if not app.security.datastore.find_user(email='adityaraj.14725832@gmail.com'):
                    app.security.datastore.create_user(
                        email='adityaraj.14725832@gmail.com',
                        password=hash_password("12345"),
                        username='adityaa@123',
                        roles=['User']
                    )
        except Exception as e:
            print(f"An error occurred while creating users: {e}")

        # Create user details
        try:
            if UserDetail.query.first() is None:
                admin = User.query.filter_by(email='bytescode0115@gmail.com').first()
                if admin:
                    detail = UserDetail(
                        user_id=admin.id,
                        first_name='Bytes',
                        last_name='Code',
                        dob=datetime(2005, 7, 15),
                        gender='male',
                        bio='I am the Super User of App.'
                    )
                    db.session.add(detail)

                user1 = User.query.filter_by(email='hanzalatafzeel44@gmail.com').first()
                if user1:
                    detail = UserDetail(
                        user_id=user1.id,
                        first_name='Hanzala',
                        last_name='Tafzeel',
                        dob=datetime(2005, 7, 15),
                        gender='male',
                        bio='I am the Test User 1 of App.'
                    )
                    db.session.add(detail)

                user2 = User.query.filter_by(email='adityaraj.14725832@gmail.com').first()
                if user2:
                    detail = UserDetail(
                        user_id=user2.id,
                        first_name='Aditya',
                        last_name='Raj',
                        dob=datetime(2005, 10, 10),
                        gender='female',
                        bio='I am the Test User 2 of App.'
                    )
                    db.session.add(detail)

                db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"An error occurred while adding user details: {e}")