# IMPORTS
from datetime import datetime
import logging
from functools import wraps

import pyotp
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm, RecaptchaField
from werkzeug.security import check_password_hash
from app import db
from lottery.views import lottery
from models import User
from users.forms import RegisterForm, LoginForm

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():

        # Check if email already in database
        user = User.query.filter_by(email=form.email.data).first()

        # If user email has an account, output as such
        if user:
            flash('Email address already exists')
            return render_template('register.html', form=form)

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        role='user', pin_key=form.pin_key)
        pin_key = form.pin_key.data,
        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # sends user to login page
        return redirect(url_for('users.login'))
    # if request method is GET or form not valid re-render signup page
    return render_template('register.html', form=form)


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # if session attribute logins does not exist create attribute logins
    if not session.get('logins'):
        session['logins'] = 0
    # if login attempts is 3 or more create an error message
    elif session.get('logins') >= 3:
        flash('Number of incorrect logins exceeded')

    form = LoginForm()

    if form.validate_on_submit():

        # Increment session login attempts
        session['logins'] += 1

        # Check user exists
        user = User.query.filter_by(email=form.email.data).first()
        if not user or not check_password_hash(user.password, form.password.data):
            # if no match create appropriate error message based on login attempts
            if session['logins'] == 3:
                flash('Number of incorrect logins exceeded')
            elif session['logins'] == 2:
                flash('Please check your login details and try again. 1 login attempt remaining')
            else:
                flash('Please check your login details and try again. 2 login attempts remaining')
            return render_template('login.html', form=form)

        if pyotp.TOTP(user.pin_key).verify(form.pin.data):
            # if user is verified reset login attempts to 0
            session['logins'] = 0
            login_user(user)

            user.last_logged_in = user.current_logged_in
            user.current_logged_in = datetime.now()
            db.session.add(user)
            db.session.commit()
        else:
            flash("You have supplied an invalid 2FA token!", "danger")
            return render_template('login.html', form=form)
        return lottery()
    return render_template('login.html', form=form)


# view user profile
@users_blueprint.route('/profile')
def profile():
    return render_template('profile.html', name="PLACEHOLDER FOR FIRSTNAME")


# view user account
@users_blueprint.route('/account')
def account():
    return render_template('account.html',
                           acc_no="PLACEHOLDER FOR USER ID",
                           email="PLACEHOLDER FOR USER EMAIL",
                           firstname="PLACEHOLDER FOR USER FIRSTNAME",
                           lastname="PLACEHOLDER FOR USER LASTNAME",
                           phone="PLACEHOLDER FOR USER PHONE")


@users_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
