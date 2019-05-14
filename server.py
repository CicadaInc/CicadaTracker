from functions import get_token
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, session, redirect
from forms import SingInForm, RegistrationForm, NewTask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Супер секретный мод на майнкрафт'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def as_dict(row):
    return dict(row.__dict__)


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


@app.route("/")
@app.route("/index")
def index():
    tasks = [as_dict(e) for e in Task.query.all()]
    return render_template("main.html", title="Cicada Tracker", tasks=tasks)


@app.route("/register")
def registration():
    form = RegistrationForm()

    if form.validate_on_submit():
        name = form.name + ' ' + form.surname + ' ' + form.patronymic
        user = User(login=form.username, password=form.password, name=name)
        db.session.add(user)
        db.session.commit()

    return render_template("registration.html", form=form, title="Регистрация")


@app.route("/login")
def login():
    form = SingInForm()

    if form.validate_on_submit():
        pass

    return render_template("login.html", form=form, title="Авторизация")


@app.route("/task/<int:id>")
def task(id):
    full_task = Task.query.filter_by(id=id).first()
    task_title = full_task.title

    return render_template("task.html", title="Просмотр задачи", task_title=task_title)


@app.route('/add_task')
def add_task():
    form = NewTask()
    return render_template("new_task.html", title="Добавление задачи", form=form)


app.run(port=8081, host='127.0.0.1')
