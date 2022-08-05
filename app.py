from datetime import datetime
from os import getenv

from flask import (Flask, render_template, request,
                   url_for, redirect, flash, session)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import InputRequired, EqualTo
from flask_bcrypt import Bcrypt


from dotenv import load_dotenv


# take environment variables from .env.
load_dotenv()


app = Flask(__name__)

# config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = getenv('FROM_SECRET_KEY')
app.secret_key = getenv('SESSION_SECRET_KEY')

# database
db = SQLAlchemy(app)


# bcrypt
bcrypt = Bcrypt()


# database user table class
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    todoId = db.relationship('Todo', backref='user', lazy=True)


# database todo table class
class Todo(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    todoId = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, unique=True,  nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow())


# form for Log in and Sign up
class RegisterForm(FlaskForm):

    name = StringField('Name', validators=[InputRequired()])
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[
        InputRequired(),
        EqualTo('conformPassword', message='Passwords must match')
    ])
    conformPassword = PasswordField('conform password')


# form for todo
class TodoForm(FlaskForm):

    title = StringField('Title', validators=[InputRequired()])
    description = TextAreaField('Description')


# home
@ app.route('/')
@ app.route('/home')
def index():

    form = RegisterForm()

    return render_template('index.html', form=form)


# signup
@ app.route('/signup', methods=['GET', 'POST'])
def signup():

    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():

        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first() != None:

            form.name.data = name
            form.username.data = username

            flash(f'This username {username} have already have a account')
            return redirect(url_for('signup'))

        hashPassword = bcrypt.generate_password_hash(password)

        db.session.add(
            User(name=name, username=username, password=hashPassword))
        db.session.commit()

        flash('Account is created successfully!')

        return redirect(url_for('login'))

    return render_template('signup.html', form=form)


# login
@ app.route('/login', methods=['GET', 'POST'])
def login():

    form = RegisterForm()

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        fetch = User.query.filter_by(username=username).first()

        if fetch == None:

            form.username.data = username

            flash(f'This username {username} account is not created')

            return redirect(url_for('login'))

        if not bcrypt.check_password_hash(fetch.password, password):

            form.username.username = username

            flash('Please check username and password')

            return redirect(url_for('login'))

        session['username'] = username

        return redirect(url_for('todo'))

    return render_template('login.html', form=form)


# add todo
@ app.route('/todo', methods=['GET', 'POST'])
def todo():

    form = TodoForm()

    sessionUsername = session['username']

    userId = User.query.filter_by(username=sessionUsername).first()

    recs = Todo.query.filter_by(todoId=userId.id).all()

    if request.method == 'POST' and form.validate_on_submit():

        # html name
        title = request.form.get('title')
        description = request.form.get('description')

        userId = User.query.filter_by(username=sessionUsername).first()

        # database insert
        db.session.add(
            Todo(todoId=userId.id, title=title, description=description))
        db.session.commit()

        flash('Your Todo is added successfully!')

        return redirect(url_for('todo'))

    return render_template('todo.html', form=form, recs=recs)


# update todo
@ app.route('/todo/update/<int:id>', methods=['GET', 'POST'])
def update(id):

    form = TodoForm()

    if request.method == 'POST':

        # html name
        title = request.form.get('title')
        description = request.form.get('description')

        # fetch
        rec = Todo.query.get_or_404(id)

        # update
        rec.title = title
        rec.description = description
        rec.datetime = datetime.utcnow()

        # commit
        db.session.commit()

        flash('Your Todo is Update successfully!')

        return redirect(url_for('todo'))

    # fetch where
    fetch = Todo.query.filter_by(id=id).first()

    form.description.data = fetch.description

    return render_template('update.html', fetch=fetch, form=form)


# delete todo
@ app.route('/todo/delete/<int:id>')
def delete(id):

    fetch = Todo.query.filter_by(id=id).first()
    db.session.delete(fetch)
    db.session.commit()

    flash('Your Todo is deleted successfully!')

    return redirect(url_for('todo'))


if __name__ == '__main__':

    app.run()
