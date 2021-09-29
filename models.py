from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import backref

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

# username, pass, e-m
class User(db.Model):
    __tablename__= 'users'

    username = db.Column(db.String(20), primary_key=True, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    feedbacks = db.relationship('Feedback', backref='users', cascade="all, delete-orphan")
    # user = db.relationship('User', backref='feedback')

    # start_register
    @classmethod
    def register(cls, username, password, email, first_name, last_name, is_admin):
        """Register User with hashed password and return user"""

        hashed = bcrypt.generate_password_hash(password)

        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name, is_admin=is_admin)
    # end_register

    # start_authenticate
    @classmethod
    def authenticate(cls, username, pwd):
        """Checks that username exists and password is correct"""

        user = User.query.filter_by(username = username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False    
    # end_authenticate    

    def delete_user(self):
        """Allows a user to delete their account"""

        db.session.delete(self)
        db.session.commit()

class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)   
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, db.ForeignKey('users.username')) 

    # user = db.relationship('User', backref='feedback')

    @classmethod
    def add_feedback(cls, title, content, username):
        """Allows users to add feedback"""

        new_feedback = Feedback(title=title, content=content, username=username)

        db.session.add(new_feedback)
        db.session.commit()

    def delete_feedback(self):
        """Allows users to delete feedback"""

        db.session.delete(self)
        db.session.commit()

    def edit_feedback(self, title, content):
        """Allows user to edit feedback"""

        self.title = title
        self.content = content

        db.session.commit()







