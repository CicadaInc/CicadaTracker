from flask import Flask, render_template, url_for, session, redirect
from forms import SingInForm, RegistrationForm

from processing import *
from API import api_app

app = Flask(__name__)
app.testing = True
app.config['SECRET_KEY'] = 'Супер секретный мод на майнкрафт'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['RESTFUL_JSON'] = {'ensure_ascii': False}
app.register_blueprint(api_app, url_prefix='/api')

init_db(app)


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


if __name__ == '__main__':
    app.run(port=8080)
