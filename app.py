from models import db, connect_db, User, Feedback
from flask import Flask, render_template, redirect, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
from forms import UserForm, LoginForm, DeleteForm, FeedbackForm
from werkzeug.exceptions import Unauthorized


app = Flask(__name__)

app.config['SECRET_KEY'] = 'secrets'
app.config['SQLALCHEMY_DATABASE_URI' ] = 'postgresql:///authentication_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['DEBUG_TB_ENABLED'] = True

debug = DebugToolbarExtension(app)

with app.app_context():
    connect_db(app)
    db.create_all()


@app.route('/')
def home_page():
    feedback = Feedback.query.all()
    return render_template("home.html", feedback=feedback)


@app.route('/register',  methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User.register(username, password, first_name, last_name, email)

        db.session.commit()
        session['username'] = user.username

        return redirect(f"/users/{user.username}")
    else:
        return render_template("register.html", form=form)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        user = User.authenticate(name, pwd)

        if user:
            session["username"] = user.username  
            return redirect(f"/users/{user.username}")
    else:
        flash ("Please try a differnt username/password")
        return render_template('login.html', form=form)
    
@app.route("/users/<username>")
def secret(username):
    """Individual user page"""
    if "username" not in session or username != session['username']:
        raise Unauthorized()
    else:
        form = DeleteForm()
        user = User.query.get(username)
        return render_template("secret.html", user=user, form=form)
    
@app.route('/users/<username>/add_feedback', methods=['GET', 'POST'])
def add_feedback(username):
    
    if "username" not in session or username != session['username']:
        raise Unauthorized()
    
    form = FeedbackForm()
    user = User.query.get(username)

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        username = username

        feedback = Feedback(title=title,
                             content=content,
                              username=username)
        
        db.session.add(feedback)
        db.session.commit()

        return redirect(f'/users/{user.username}')
    
    else:
        
        return render_template("feedback_form.html", form=form, user=user)
    
@app.route('/users/<feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()
    
    feedback = Feedback.query.get(feedback_id)
    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
    return redirect(f'/users/{feedback.username}')

@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()
    
    form = FeedbackForm(obj=feedback)


    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")
    else:
        return render_template('edit.html', feedback=feedback, form=form)


    
@app.route("/logout")
def logout():
    """Logs the user out and redirects to homepage."""

    session.pop("username")

    return redirect("/")

