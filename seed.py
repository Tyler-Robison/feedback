"""Seed file to make sample data for pets db."""

from flask.globals import session
from models import User, Feedback, db
from app import app

# Create all tables
db.drop_all()
db.create_all()

# If table isn't empty, empty it
User.query.delete()
Feedback.query.delete()

# Add users
u1 = User.register('Bobo758', 'bob758', 'bob@gmail.com','Bob', 'Smith', False)
u2 = User.register('Freddy', 'fred758', 'fred@gmail.com', 'Fred', 'Durst', False)
u3 = User.register('Tyler', 'tyler758', 'tyle@gmail.com', 'Tyler', 'Robison', True)
u4 = User.register('ChickenGal', 'chicken758', 'chicken@yahoo.com', 'Jane', 'Green', False)


f1 = Feedback(title='I hate you', content='So much', username='Bobo758')
f2 = Feedback(title='I love you', content='A lot', username='Bobo758')
f3 = Feedback(title='I like turtle', content='they are green', username='Bobo758')
f4 = Feedback(title='Hi', content='I said hi!', username='Freddy')
f5 = Feedback(title='Bye', content='Goodbye', username='Tyler')
f6 = Feedback(title='Got no time', content='For that', username='ChickenGal')
f7 = Feedback(title='Found more time', content='In the attic', username='ChickenGal')

db.session.add_all([u1, u2, u3, u4])
db.session.commit()

db.session.add_all([f1, f2, f3, f4, f5, f6, f7])
db.session.commit()