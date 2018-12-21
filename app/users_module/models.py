
from app import db, app
import datetime
from flask_user import UserMixin


# Base model for all other database classes to inherit
class Base(db.Model):

    __abstract__ = True

    id            = db.Column(db.Integer, primary_key=True)


class User(Base, UserMixin):
    __tablename__ = 'users'
    active = db.Column('is_active3', db.Boolean(), nullable=False, server_default='1')

    # User authentication information.
    email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

    # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='user_roles')

class Role(Base):
    __tablename__ = 'roles'
    name = db.Column(db.String(50), unique=True)

class UserRoles(Base):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

