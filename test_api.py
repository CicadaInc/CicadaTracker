import requests
from server import *

url = 'http://localhost:8080/api/'

print(requests.get(url+'task').json())
print(requests.get(url+'task?token=None').json())