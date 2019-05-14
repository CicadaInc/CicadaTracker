from random import choice
from string import ascii_letters, digits


def get_token():
    res = ''
    symbols = ascii_letters + digits
    for i in range(32):
        res += choice(symbols)
    return res
