from processing import *
import os

from flask import Blueprint, send_file, request, jsonify, session, current_app
from werkzeug.utils import secure_filename

from flask_restful import Api, Resource

api_app = Blueprint('API', __name__)
api = Api(api_app)
current_app.config['JSON_AS_ASCII'] = False
current_app.config['RESTFUL_JSON'] = {'ensure_ascii': False}
current_app.register_blueprint(api_app, url_prefix='/api')


def abort_json(code, msg):
    return {'code': code, 'error': msg, 'success': False}, code


class Task(Resource):
    def get(self, tid=None):
        token = get_token()
        if token:
            if token_valid():
                if tid is not None:
                    pass
                else:
                    pass
            else:
                return abort_json(403, 'Invalid token')
        else:
            return abort_json(403, 'Token required')

    def post(self):
        token = get_token()
        if token:
            if token_valid():
                pass
            else:
                return abort_json(403, 'Invalid token')
        else:
            return abort_json(403, 'Token required')

    def put(self, tid):
        token = get_token()
        if token:
            if token_valid():
                if tid is not None:
                    pass
                else:
                    return abort_json(404, 'Task id required')
            else:
                return abort_json(403, 'Invalid token')
        else:
            return abort_json(403, 'Token required')

    def delete(self, tid):
        token = get_token()
        if token:
            if token_valid():
                if tid is not None:
                    pass
                else:
                    return abort_json(404, 'Task id required')
            else:
                return abort_json(403, 'Invalid token')
        else:
            return abort_json(403, 'Token required')


api.add_resource(Task, '/task')
api.add_resource(Task, '/task/<int:pid>')
