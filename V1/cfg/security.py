from .config import Config
from .user import User as usr


from uuid import uuid4
from cryptography.fernet import Fernet
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import Flask, render_template, request, session
from flask_session import Session
import sqlite3
import datetime
import math
import json


# cryptography stuff from https://nitratine.net/blog/post/encryption-and-decryption-in-python/
# python -m pip install cryptography

# session stuff : https://pythonhosted.org/Flask-Session/
class AppSecure:
    def __init__(self):
        # ---- KEYS FOR SESSIONS AND SUCH
        self.app_key = "AppK"
        self.user_key = "UsrK"
        self.ses_key = "SessK"
        self.user_data_key = "UsrD"

    def debugSession(self):
        if Config.DEBUG:
            for key in session.keys():
                Config.debug(f"KEY: {key} -> {session.get(key)}")

    def generateKey(self,keyName):
        if session.get(keyName):
            return session.get(keyName)

        password = Config.getAppKey(Config.KEY_FILE)
        # This is input in the form of a string
        if not isinstance(password, bytes):
            password = password.encode()  # Convert to type bytes

        salt = uuid4().bytes  # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        session[keyName] = key
        return key

    def getSessionKey(self):
        if not session.get(self.ses_key):
            session[self.ses_key] = self.generateKey(self.ses_key)

        sessionKey = session.get(f"{self.ses_key}")

        Config.debug(f"getsessionkey: {self.ses_key} : {sessionKey}")
        return sessionKey

    def clearSession(self):
        Config.debug("Clearing Session")
        # [session.pop(key) for key in list(session.keys()) if key != '_flashes']
        session.clear()

    def clearSessionVar(self,key):
        Config.debug(f"Clear {key}")
        session.pop(key)

    def generateAppKeys(self):
        _appKey = self.getAppKey()
        _sessionKey = self.generateKey(self.ses_key)
        _userKey = self.generateKey(self.user_key)
        if not session.get(self.er_data_key):
            session[self.user_data_key] = usr.User.getUser()
        _userData = session.get(self.user_data_key)

        print(f"{self.ses_key}  {_sessionKey}")
        # add to session using hash

        session[f"{self.app_key}"] = _appKey
        session[f"{self.ses_key}"] = _sessionKey
        session[f"{self.user_key}"] = _userKey
        self.setSessionVar(self.user_data_key, _userData)
        # session[f"{user_data_key}"] = _userData

        # debug(f"session[{app_key}] : {session[app_key]}")
        # debug(f"session[{ses_key}] : {session[ses_key]}")



    def setSessionVar(self, key, value):
        Config.debug(f"SETTING SESSION VAR {key} : {value}")
        _sessionKey = self.getSessionKey()
        _value = value
        if not isinstance(value, str):
            if (isinstance(value, list)) or (isinstance(value, dict)):
                Config.debug(f"json dums : {value}")
                _value = json.dumps(value)
        else:
            Config.debug(f"SET TYPE: {type(value)}")
            _value = value

        f = Fernet(_sessionKey)
        if not isinstance(_value, bytes):
            _value = _value.encode()

        encrypted = f.encrypt(_value)

        session[key] = encrypted
        Config.debug(f"seting: {key} : {key} : {encrypted}")

    def getSessionVar(self, key):
        _key = key
        sessionKey = self.getSessionKey()
        f = Fernet(sessionKey)
        if session.get(_key):
            encrypted = session.get(_key)
            if not isinstance(encrypted, bytes):
                encrypted = encrypted.encode()

            decrypted = f.decrypt(encrypted)
            Config.debug(f"Type: {type(decrypted)}")
            Config.debug(f"get: {key} : {_key} : {decrypted}")
            if isinstance(decrypted, bytes):
                decrypted = decrypted.decode()
            return decrypted
        return False