from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from processing import *
from API import api_app

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Супер секретный мод на майнкрафт'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['RESTFUL_JSON'] = {'ensure_ascii': False}
app.register_blueprint(api_app, url_prefix='/api')

if __name__ == '__main__':
    init_db(app)
    app.run(port=8080)
