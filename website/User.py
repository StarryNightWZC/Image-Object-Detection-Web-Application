import flask_login
from flask_login import UserMixin
from sqlalchemy import Column,String
from sqlalchemy.ext.declarative import declarative_base

from website import db, login_manager

@login_manager.user_loader
def load_user(email):
    print(User.query.filter_by(email=email).first())
    return User.query.filter_by(email=email).first()

class User(UserMixin,db.Model):
        # 表的名字:
        __tablename__ = 'testtable'
        email = db.Column(db.String(100), primary_key=True)
        password=db.Column(db.String(100))
        username=db.Column(db.String(100))
        loggedin=False

        def __repr__(self):
                return "User('{self.username}')"

        def get_id(self):
                return (self.email)

        def get_username(self):
                return (self.username)


