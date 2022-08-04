from datetime import datetime
from os import getenv

from flask import (Flask, render_template, request,
                   url_for, redirect, flash)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired


app = Flask(__name__)

# config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = getenv('SECRET_KEY')

# database
db = SQLAlchemy(app)

# database class


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, unique=True,  nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow())


# form
class MyForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    description = TextAreaField('Description')


# home
@app.route('/')
@app.route('/home')
def index():

    form = MyForm()
    recs = Todo.query.filter().all()

    return render_template('index.html', form=form, recs=recs)


# add todo
@app.route('/todo', methods=['POST'])
def todo():

    # html name
    title = request.form.get('title')
    description = request.form.get('description')

    # database insert
    db.session.add(Todo(title=title, description=description))
    db.session.commit()

    flash('Your Todo is added successfully!')

    return redirect(url_for('index'))


# update todo
@app.route('/todo/update/<int:id>', methods=['GET', 'POST'])
def update(id):

    form = MyForm()

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

        return redirect(url_for('index'))

    # fetch where
    fetch = Todo.query.filter_by(id=id).first()

    form.description.data = fetch.description

    return render_template('update.html', fetch=fetch, form=form)


# delete todo
@app.route('/todo/delete/<int:id>')
def delete(id):

    fetch = Todo.query.filter_by(id=id).first()
    db.session.delete(fetch)
    db.session.commit()

    flash('Your Todo is deleted successfully!')

    return redirect(url_for('index'))


if __name__ == '__main__':

    app.run(port=8000, debug=True)
