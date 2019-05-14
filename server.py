from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from functions import get_token
from wtforms import StringField, PasswordField, SubmitField
from flask import Flask, render_template, url_for, session, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Супер секретный мод на майнкрафт'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(80), unique=True, nullable=False, default=get_token)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return '<User {} {} {} {} [}>'.format(
            self.id, self.login, self.name, self.password, self.token)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000), unique=False, nullable=False)
    status = db.Column(db.String(50), unique=False, nullable=False)
    category = db.Column(db.String(80), unique=False, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('Task', lazy=True))

    def __repr__(self):
        return '<Task {} {} {} {} {} {}>'.format(
            self.id, self.title, self.status, self.category, self.author_id, self.author)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(80), unique=False, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('Comment', lazy=True))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    task = db.relationship('Task', backref=db.backref('Comment', lazy=True))

    def __repr__(self):
        return '<Task {} {} {} {} {} {}>'.format(
            self.id, self.content, self.author_id, self.author, self.task_id, self.task)


db.create_all()


class SingInForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    surname = StringField(validators=[DataRequired()])
    patronymic = StringField(validators=[DataRequired()])
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    password_confirm = PasswordField(validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


@app.route("/")
@app.route("/index")
def index():
    return render_template("base.html", title="Cicada Tracker")


@app.route("/register")
def registration():
    form = RegistrationForm()
    return render_template("registration.html", form=form, title="Регистрация")


@app.route("/login")
def login():
    form = SingInForm()
    return render_template("login.html", form=form, title="Авторизация")


app.run(port=8081, host='127.0.0.1')
