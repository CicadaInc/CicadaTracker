import requests
from server import *


url = 'http://localhost:8080/api/'

if not User.query.first():
    u = User(login='login', name='name', password='password')
    db.session.add(u)
    db.session.commit()
else:
    u = User.query.first()
print(as_dict(u))
print(requests.get(url+'task').json())
print(requests.get(url+'task?token=None').json())
print(requests.get(url+'task', params={'token': u.token}).json())
print()
print(requests.post(url+'task?token=None', json={}).json())
print(requests.post(url+'task', json={}, params={'token': u.token}).json())
r = requests.post(url+'task', json={'title': 'It works!'}, params={'token': u.token}).json()
print(r)
r = requests.get(url+'task', params={'token': u.token}).json()
print(r)
r = r['data'][0]
print(requests.get(url+'task/'+str(r['id']), params={'token': u.token}).json())
print()
requests.put(url+'task/'+str(r['id']), params={'token': u.token}, json={'title': 'other title', 'worker_id': 0})
print(requests.get(url+'task', params={'token': u.token}).json())
print()
print(requests.delete(url+'task/'+str(236327238236237236723732)).json())
print(requests.delete(url+'task/'+str(r['id'])).json())
print(requests.delete(url+'task/'+str(r['id']), params={'token': u.token}).json())