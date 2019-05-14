from flask import request, session, redirect, abort
from flask import current_app as app
from functools import wraps

DATABASE = 'data.db'


def get_cuid():
    return session.get('user_id', None)


def get_token():
    return request.args.get('token', session.get('token', None))


def token_valid():
    return True


def login_required(api=False):
    def login_required_dec(f):
        @wraps(f)
        def login_required_wrapper(*args, **kwargs):
            if not get_cuid():
                ref = request.headers.get('referer', 'index')
                if ref.endswith('login') or ref.endswith('register') or ref.endswith('logout'):
                    return redirect('index')
                else:
                    session['back'] = 'index'
                    session['next'] = request.url
                    return redirect('login')
            else:
                if not api:
                    abort(410)
                else:
                    return {'success': False, 'error': 'Доступ ограничен'}

        return login_required_wrapper

    return login_required_dec