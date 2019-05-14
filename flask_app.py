from flask import Flask, request

from APIs import GeoApi, MapsApi, SearchApi
from dialog_json_handler import Storage, Response, Button, Card
from input_parser import Sentence
from settings import logging, log_object
from server import db, Task, User
import time
import requests

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

hint = ''
url = 'http://127.0.0.1:8080/api/'.format('176.59.34.121')


@app.errorhandler(404)
def error_404(*args):
    logging.error('404')
    logging.error(request.url)
    logging.error(str(dict(request.headers)))
    logging.error(log_object(request.json))


@app.route('/post', methods=['POST'])
def request_handler():
    data = request.json
    resp = dialog(data)
    return resp.send()


def dialog(data):
    logging.info('-----------DIALOG-----------')
    if data['session']['new']:
        Storage.remove(data['session']['user_id'])
    user = Storage(data)
    resp = Response(data)
    logging.info('CONTINUE ' + str(user.id))
    logging.info('INPUT ' + log_object(user.request))
    logging.info('STATE ' + str(user.state) + ' ' + str(user.state_init) + ' DELAY ' + str(user.delay))
    logging.info('TYPE ' + str(user.type))
    logging.info('STORAGE ' + str(id(user)) + ' ' + log_object(user.data))

    user.pre_step()
    result = handle_state(user, resp)
    user.post_step()
    return result


def handle_state(user, resp):
    if user.type == 'SimpleUtterance':
        sent = Sentence(user.text)
        ag, dg = sent.agreement

        if user.state == 0:
            if user.delay == 0:
                user.init_state()
                resp.msg('Укажите свой логин и пароль через пробел')
            else:
                spl = user.text.split(' ')
                if len(spl) == 2:
                    u = User.query.filter_by(login=spl[0], password=spl[1]).first()
                    if u:
                        user['token'] = u.token
                        user['id'] = u.id
                    else:
                        resp.ms('Пользователь не найден')
                else:
                    resp.msg('Недопустимый формат ввода')
            user.delay_up()

        else:
            if user.delay == 0:
                user.init_state()
                resp.msg('Приветствую! Что вы хотите узнать?')
            else:
                if sent.word_collision('задача'):
                    nums = user.entity(t='number')
                    if nums:
                        tid = int(nums[0])
                        task = Task.query.filter_by(id=tid).filter_by(author_id=user['id']).first()
                        if task:
                            resp.msg('Всё ок')
                        else:
                            resp.msg('Задание не найдено')
                    else:
                        tasks = Task.query.filter_by(author_id=user['id']).all()
                        if tasks:
                            for t in tasks:
                                resp.msg('Задача {id} "{title}"\n   Дедлайн: {time}'.format(**{
                                    'id': t.id,
                                    'title': t.title,
                                    'time': time.asctime(t.time)
                                }))
                        else:
                            resp.msg('Нет задаий')
            user.delay_up()


    elif user.type == 'ButtonPressed':
        if user.payload:
            pl = user.payload
            action = pl.get('action')
            if action == 'map':
                resp.text = 'Показать карту не удалось'
                btn = Button(user, 'map_url', 'Показать на Яндекс.Картах', url=pl['url'])
                img = user.upload_image('map', pl['image_url'])
                if img:
                    card = Card(user, '', img)
                    card['button'] = btn.send()
                    card['title'] = btn['title']
                    user.add_card(card)
                else:
                    user.add_button(btn)
            elif 'input' in pl:
                user.type = 'SimpleUtterance'
                user.text = pl['input']
                return handle_state(user, resp)
        else:
            resp.text = 'Выполняю'

    return resp
