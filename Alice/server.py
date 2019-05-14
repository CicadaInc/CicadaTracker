from flask import Flask, request

from APIs import GeoApi, MapsApi, SearchApi
from dialog_json_handler import Storage, Response, Button, Card
from input_parser import Sentence
from settings import logging, log_object
import time

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

hint = ''
url = 'http://{}:8080/api/'.format('176.59.34.121')


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
                    response = request.post(url + 'auth', json={'login': spl[0], 'password': spl[1]}).json()
                    data = response.get('data', {})
                    if response.get('success', False):
                        user['token'] = data['token']
                        user.state = 1
                    else:
                        resp.ms('Произошла ошибка\n' + response['error'])
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
                        response = request.get(url + 'task/' + str(tid), params={'token': user['token']}).json()
                        log_object(response)
                        if response['success']:
                            data = response['data']
                        else:
                            resp.msg('Ошибка\n' + response['error'])
                    else:
                        response = request.get(url + 'task', params={'token': user['token']}).json()
                        log_object(response)
                        if response['success']:
                            tasks = response['data']
                            for t in tasks:
                                resp.msg('Задача {id} "{title}"\n   Дедлайн: {time}'.format(**{
                                    'id': t['id'],
                                    'title': t['title'],
                                    'time': time.asctime(time.localtime())
                                }))
                        else:
                            resp.msg('Ошибка\n' + response['error'])
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
