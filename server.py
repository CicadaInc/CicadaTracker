from flask import Flask, render_template, url_for, session, redirect
from forms import SingInForm, RegistrationForm, NewTask

from processing import *
from API import api_app

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Супер секретный мод на майнкрафт'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['RESTFUL_JSON'] = {'ensure_ascii': False}
app.register_blueprint(api_app, url_prefix='/api')


@app.route("/")
@app.route("/index")
def index():
    if session.get('user_id', None):
        tasks = [as_dict(e) for e in Task.query.all()]
        rights = User.query.filter_by(id=session['user_id']).first().rights
        if rights != 'Админ':
            return render_template("main.html", title="Cicada Tracker", tasks=tasks)
        else:
            return render_template("admin.html", title="Cicada Tracker")
    return redirect('/login')


@app.route("/users")
def users():
    users_list = User.query.all()

    return render_template("users.html", title="База пользователей", users=users_list)


@app.route("/add_admin/<int:id>")
def add_admin(id):
    user = User.query.filter_by(id=id).first()
    user.rights = 'Админ'
    db.session.commit()

    return redirect("/users")


@app.route("/ban/<int:id>")
def ban(id):
    user = User.query.filter_by(id=id).first()
    user.rights = 'Забанен'
    db.session.commit()

    return redirect("/users")


@app.route("/register", methods=['POST', 'GET'])
def registration():
    form = RegistrationForm()

    if form.validate_on_submit():
        if not User.query.filter_by(login=form.username.data).first() \
                and form.password.data == form.password_confirm.data:
            name = form.name.data + ' ' + form.surname.data + ' ' + form.patronymic.data
            user = User(login=form.username.data, password=form.password.data, name=name, rights='Пользователь')
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
    task_title = full_task.title

    return render_template("task.html", title="Просмотр задачи", task_title=task_title)


@app.route('/add_task')
def add_task():
    form = NewTask()
    return render_template("new_task.html", title="Добавление задачи", form=form)


if __name__ == '__main__':
    init_db(app)
    app.run(port=8080)
