import base64
import copy
from datetime import datetime
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
from cryptography.fernet import Fernet
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash
from app import db


def encrypt(data, draw_key):
    return Fernet(draw_key).encrypt(bytes(data, 'utf-8'))


def decrypt(data, draw_key):
    return Fernet(draw_key).decrypt(data).decode("utf-8")


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    # User activity information
    registered_on = db.Column(db.DateTime, nullable=True)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')

    # crypto key for user's lottery draws
    draw_key = db.Column(db.BLOB)
    pin_key = db.Column(db.String(100), nullable=False)

    # Define the relationship to Draw
    draws = db.relationship('Draw')

    def __init__(self, email, password, firstname, lastname, phone, role, pin_key):
        self.email = email
        self.password = generate_password_hash(password)
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.draw_key = base64.urlsafe_b64encode(scrypt(password, str(get_random_bytes(32)), 32, N=2 ** 14, r=8, p=1))
        self.role = role
        self.pin_key = pin_key
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = None


class Draw(db.Model):
    __tablename__ = 'draws'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    draw = db.Column(db.String(100), nullable=False)
    played = db.Column(db.BOOLEAN, nullable=False, default=False)
    match = db.Column(db.BOOLEAN, nullable=False, default=False)
    win = db.Column(db.BOOLEAN, nullable=False)
    round = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, user_id, draw, win, round, draw_key):
        self.user_id = user_id
        self.draw = encrypt(draw, draw_key)
        self.played = False
        self.match = False
        self.win = win
        self.round = round

    # Decrypt draw info for checking win
    def view_draw(self, draw_key):
        draw_copy = copy.deepcopy(self)
        return decrypt(draw_copy, draw_key)


# Initialises the Database with a test user
def init_db():
    db.drop_all()
    db.create_all()
    new_user = User(email='user1@test.com', password='Password1!',
                    firstname='Alice', lastname='Jones', phone='0191-123-4567', role='admin',
                    pin_key='EN3YARJVZDMPEG44Z4MIZU4F4YKKMEIV')

    db.session.add(new_user)
    db.session.commit()
