from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  render_template_string
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_login import login_user, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash

from app.users_module.models import User
from app import db, redis_server, login_manager
users_routes = Blueprint('users', __name__, url_prefix='/users')



class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=32)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email      = StringField('email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=60)])
    username   = StringField('username', validators=[InputRequired(), Length(min=4, max=16)])
    password   = PasswordField('password', validators=[InputRequired(), Length(min=4, max=32)])

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
        new_user = User(email=form.email.data, password=hashed_password, username=form.username.data)
        db.session.add(new_user)
        db.session.commit()
        flash("New User Created - Please Login")
        return redirect('users/login')
    else:
        pass
    return render_template('users/signup.html', form=form)

@users_routes.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return render_template('search/dunderbands.html')
