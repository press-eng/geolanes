import jwt

from lib import config


def encode(object):
    return jwt.encode(object, config.JWT_SECRET, algorithm="HS256")


def decode(token):
    return jwt.decode(token, config.JWT_SECRET, algorithms="HS256")
