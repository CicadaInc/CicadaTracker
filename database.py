from flask_sqlalchemy import SQLAlchemy
from random import choice
from string import ascii_letters, digits


def create_token():
    res = ''
    symbols = ascii_letters + digits
    for i in range(32):
        res += choice(symbols)
    return res


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(80), unique=True, nullable=False, default=create_token)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    rights = db.Column(db.String(80), unique=False, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return '<User {} {} {}>'.format(
            self.id, self.login, self.name)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000), unique=False, nullable=False)
    status = db.Column(db.String(50), unique=False, nullable=False)
    category = db.Column(db.String(80), unique=False, nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Task {} {} {} {} {}>'.format(
            self.id, self.title, self.status, self.author_id, self.author)


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


def init_db(app):
    db.init_app(app)
    db.app = app
    db.create_all(app=app)
