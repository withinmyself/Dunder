from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  render_template_string
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_user import roles_required, forms
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash

from app.users_module.models import User, Role, UserRoles
from app import app, db, redis_server
users_routes = Blueprint('users', __name__, url_prefix='/users')
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'



class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=32)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email      = StringField('email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=60)])
    first_name = StringField('first_name', validators=[InputRequired(), Length(min=1, max=15)])
    last_name  = StringField('last_name', validators=[InputRequired(), Length(min=4, max=15)])
    password   = PasswordField('password', validators=[InputRequired(), Length(min=6, max=32)])

@login_manager.user_loader
def load_user(user_id):
    user =  db.session.query(User).filter_by(id=user_id).first()
    return user


@users_routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit:
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return render_template('search/dunderbands.html')
    return render_template('users/login.html', form=form)

@users_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        username = '{0}{1}'.format(form.first_name.data[:-len(form.first_name.data)+1].lower(), form.last_name.data.lower())
        new_user = User(email=form.email.data, password=hashed_password,
                        first_name=form.first_name.data, last_name=form.last_name.data,
                        username=username)
        db.session.add(new_user)
        db.session.commit()
        return '<h1>New User Has Been Created!</h1>'
    return render_template('users/signup.html', form=form)
@users_routes.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return render_template('search/dunderbands.html')
