from functions import get_token
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, session, redirect
from forms import SingInForm, RegistrationForm

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


@app.route("/register", methods=['POST', 'GET'])
def registration():
    form = RegistrationForm()

    if form.validate_on_submit():
        if not User.query.filter_by(login=form.username.data).first() \
                and form.password.data == form.password_confirm.data:
            name = form.name.data + ' ' + form.surname.data + ' ' + form.patronymic.data
            user = User(login=form.username.data, password=form.password.data, name=name)
            db.session.add(user)
            db.session.commit()
            return redirect("/login")

    return render_template("registration.html", form=form, title="Регистрация")


@app.route("/login", methods=['POST', 'GET'])
def login():
    form = SingInForm()

    if form.validate_on_submit():
        user = User.query.filter_by(login=form.username.data).filter_by(password=form.password.data).first()
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['token'] = user.token
            print(session['user_id'])
            return redirect("/index")

    return render_template("login.html", form=form, title="Авторизация")


@app.route("/task/<int:id>")
def task(id):
    full_task = Task.query.filter_by(id=id).first()
    print(full_task.title)

    return render_template("single_task", title="Просмотр задачи")


app.run(port=8081, host='127.0.0.1')
