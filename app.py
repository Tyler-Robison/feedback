from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import Feedback, connect_db, db, User
from forms import EditFeedbackForm, LoginForm, RegisterForm, LogoutForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_proj"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def homepage():
    """Redirects to register"""

    return redirect('/register')


@app.route('/register', methods=["POST", "GET"])
def register():
    """Allows user to register"""

    if "user_id" in session:
        flash('Already registered')
        return redirect('/logout')

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        # try:
        new_user = User.register(
            username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()
        # except:
        #     db.session.rollback()
        #     flash('Registration failed, need unique username')
        #     return redirect('/register')

        session["user_id"] = new_user.username
        flash('Account Created!')

        return redirect(f'/users/{username}')

    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=["POST", "GET"])
def login():
    """Allows user to login"""

    if "user_id" in session:
        flash('Already logged in')
        return redirect('/logout')

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session["user_id"] = user.username
            flash('Logged in!')
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)


@app.route('/logout', methods=["GET", "POST"])
def logout():
    """Logs out a user"""

    form = LogoutForm()

    if form.validate_on_submit():
        session.pop('user_id')
        flash('Goodbye')
        return redirect('/')

    return render_template('logout.html', form=form)


@app.route('/users/<username>')
def display_user_info(username):
    """Allows logged in users to see their info"""

    username = session.get('user_id')
    feedbacks = Feedback.query.filter_by()

    if username:
        user = User.query.filter_by(username=username).first()
        return render_template('users.html', user=user, feedbacks=feedbacks)
    else:
        flash('Must be logged in to access user info!')
        return redirect('/register')


@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    """Allows user to add feedback"""

    if "user_id" not in session:
        flash('Not logged in')
        return redirect('/login')

    if session['user_id'] != username:
        flash('Not your feedback')
        return redirect(f'/users/{session["user_id"]}')

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        username = session.get('user_id')

        Feedback.add_feedback(title, content, username)
        flash('Feedback added')
        return redirect(f'/users/{username}')

    return render_template('add_feedback.html', form=form)


@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """Allows user to delete feedback"""

    if "user_id" not in session:
        flash('Not logged in')
        return redirect('/login')

    feedback = Feedback.query.get_or_404(feedback_id)

    if session['user_id'] != feedback.username:
        flash('Can only delete your own feedback')
        return redirect(f'/users/{session["user_id"]}')

    feedback.delete_feedback()

    return redirect(f'/users/{feedback.username}')


@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def edit_feedback(feedback_id):
    """"Allows users to edit feedback"""

    if "user_id" not in session:
        flash('Not logged in')
        return redirect('/login')

    feedback = Feedback.query.get_or_404(feedback_id)

    if session['user_id'] != feedback.username:
        flash('Can only edit your own feedback')
        return redirect(f'/users/{session["user_id"]}')

    form = EditFeedbackForm(obj=feedback)

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback.edit_feedback(title, content)
        flash('Feedback edited')
        return redirect(f'/users/{feedback.username}')

    else:
        return render_template('edit_feedback.html', form=form)


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Allows logged in users to delete their account"""

    if "user_id" not in session:
        flash('Not logged in')
        return redirect('/login')

    if session['user_id'] != username:
        flash('Can only delete your own account!')
        return redirect(f'/users/{session["user_id"]}')

    user = User.query.filter_by(username=username).first()
    user.delete_user()

    return redirect('/')

@app.route('/admin/<username>', methods=["GET", "POST"])
def show_admin_panel(username):    
    """Allows admins to view all feedback and delete or edit any of them"""

    if "user_id" not in session:
        flash('Not logged in')
        return redirect('/login')

    admin = User.query.filter_by(username=username).first()

    if admin.is_admin == False:
        flash('Not an admin!')
        return redirect(f'/users/{session["user_id"]}')

    all_users = User.query.all()
    all_feedback = Feedback.query.all()

    return render_template('admin.html',admin=admin, all_feedback=all_feedback, all_users=all_users)

@app.route('/admin/<admin_id>/<username>/delete', methods=["POST"])        
def admin_user_delete(admin_id, username):
    """Allows admins to delete any user"""

    if "user_id" not in session:
        flash('Not logged in')
        return redirect('/login')

    admin = User.query.filter_by(username=admin_id).first()

    if admin.is_admin == False:
        flash('Not an admin!')
        return redirect(f'/users/{session["user_id"]}')

    user = User.query.filter_by(username=username).first()
    user.delete_user()    



    return redirect(f'/admin/{admin.username}')    