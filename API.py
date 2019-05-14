import os

from flask import Blueprint, send_file, request, jsonify, session, current_app
from werkzeug.utils import secure_filename

from flask_restful import Api, Resource
from processing import get_token, User, Task, as_dict, db

api_app = Blueprint('API', __name__)
api = Api(api_app)


def abort_json(code, msg):
    return {'code': code, 'error': msg, 'success': False}, code


@api_app.route('auth', methods=['POST'])
def auth():
    data = request.json
    login = data.get('login', None)
    password = data.get('password', None)
    if not login or not password:
        return abort_json(400, 'Login or password isnt supplied')
    q = User.query.filter_by(login=login).filter_by(password=password).first()
    if q:
        return {'error': '', 'success': True, 'token': q.token}
    else:
        return abort_json(404, 'User not found')


class TaskResource(Resource):
    def get(self, tid=None):
        token = get_token()
        if token:
            user = User.query.filter_by(token=token).first()
            if user:
                if tid is not None:
                    task = Task.query.filter_by(id=tid).filter_by(author_id=user.id).first()
                    if task:
                        return as_dict(task)
                    else:
                        return abort_json(404, 'Task not found')
                else:
                    return {'success': True,
                            'data': [as_dict(e) for e in Task.query.filter_by(author_id=user.id).all()],
                            'error': ''}
            else:
                return abort_json(403, 'Invalid token')
        else:
            return abort_json(403, 'Token required')

    def post(self):
        token = get_token()
        if token:
            user = User.query.filter_by(token=token).first()
            data = request.json
            if user:
                error = []
                if not data or 'title' not in data:
                    return abort_json(400, 'Title required')
                task = Task(title=data['title'],
                            status=data.get('status', 'created'),
                            author_id=user.id,
                            worker_id=data.get('worker_id', None))
                db.session.add(task)
                db.session.commit()
                return {'success': True, 'error': '', 'data': as_dict(task)}
            else:
                return abort_json(403, 'Invalid token')
        else:
            return abort_json(403, 'Token required')

    def put(self, tid):
        token = get_token()
        if token:
            user = User.query.filter_by(token=token).first()
            if user:
                if tid is not None:
                    task = Task.query.filter_by(id=tid).filter_by(author_id=user.id).first()
                    if task:
                        data = request.json
                        if data:
                            for k in ['title', 'status', 'worker_id', 'author_id']:
                                if k in data:
                                    setattr(task, k, data[k])
                            db.session.commit()
                            return {'success': True, 'error': '', 'data': as_dict(task)}
                        else:
                            return abort_json(400, 'Invalid request')
                    else:
                        return abort_json(404, 'Task not found')
                else:
                    return abort_json(400, 'Task id required')
            else:
                return abort_json(403, 'Invalid token')
        else:
            return abort_json(403, 'Token required')

    def delete(self, tid):
        token = get_token()
        if token:
            user = User.query.filter_by(token=token).first()
            if user:
                if tid is not None:
                    task = Task.query.filter_by(id=tid).first()
                    if task:
                        task.hidden = True
                        # db.session.delete(task)
                        db.session.commit()
                        return {'success': True, 'error': ''}
                    else:
                        return abort_json(404, 'Task not found')
                else:
                    return abort_json(400, 'Task id required')
            else:
                return abort_json(403, 'Invalid token')
        else:
            return abort_json(403, 'Token required')


api.add_resource(TaskResource, '/task', '/task/<int:tid>')
