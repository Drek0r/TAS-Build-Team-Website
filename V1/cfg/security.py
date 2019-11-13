from .config import Config as cfg
from .user import *


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
        self.needKeys = True
        # self.generateAppKeys()

    def debugSession(self):
        if cfg.DEBUG:
            for key in session.keys():
                cfg.debug(f"KEY: {key} -> {session.get(key)}", True)

    def generateKey(self,keyName):
        if session.get(keyName):
            return session.get(keyName)

        password = cfg.getAppKey(cfg.KEY_FILE)
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

        cfg.debug(f"getsessionkey: {self.ses_key} : {sessionKey}", True)
        return sessionKey

    def clearSession(self):
        cfg.debug("Clearing Session", True)
        # [session.pop(key) for key in list(session.keys()) if key != '_flashes']
        session.clear()

    def clearSessionVar(self,key):
        cfg.debug(f"Clear {key}", True)
        session.pop(key)

    def generateAppKeys(self):
        if self.needKeys:
            _appKey = self.getAppKey()
            _sessionKey = self.generateKey(self.ses_key)
            _userKey = self.generateKey(self.user_key)
            if not session.get(self.user_data_key):
                session[self.user_data_key] = clearUserData()
            _userData = session.get(self.user_data_key)

            cfg.debug(f"{self.ses_key}  {_sessionKey}",True)
            # add to session using hash

            session[f"{self.app_key}"] = _appKey
            session[f"{self.ses_key}"] = _sessionKey
            session[f"{self.user_key}"] = _userKey
            self.setSessionVar(self.user_data_key, _userData)
            # session[f"{user_data_key}"] = _userData

            # debug(f"session[{app_key}] : {session[app_key]}")
            # debug(f"session[{ses_key}] : {session[ses_key]}")
            self.needKeys = False


    def setSessionVar(self, key, value):
        cfg.debug(f"SETTING SESSION VAR {key} : {value}", True)
        _sessionKey = self.getSessionKey()
        _value = value
        if not isinstance(value, str):
            if (isinstance(value, list)) or (isinstance(value, dict)):
                cfg.debug(f"json dums : {value}", True)
                _value = json.dumps(value)
        else:
            cfg.debug(f"SET TYPE: {type(value)}", True)
            _value = value

        f = Fernet(_sessionKey)
        if not isinstance(_value, bytes):
            _value = _value.encode()

        encrypted = f.encrypt(_value)

        session[key] = encrypted
        cfg.debug(f"seting: {key} : {key} : {encrypted}", True)

    def getSessionVar(self, key):
        print(f"Getting session var: {key}")
        _key = key
        sessionKey = self.getSessionKey()
        f = Fernet(sessionKey)

        if session.get(_key):
            encrypted = session.get(_key)
            if not isinstance(encrypted, bytes):
                encrypted = encrypted.encode()

            decrypted = f.decrypt(encrypted)
            cfg.debug(f"Type: {type(decrypted)}", True)

            cfg.debug(f"get: {key} : {_key} : {decrypted}", True)
            if isinstance(decrypted, bytes):
                decrypted = decrypted.decode()
            return decrypted

        else:

            return False

    def isLoggedIn(self):
        if self.getSessionVar(self.user_data_key):
            usr = self.getUserSession()#json.dumps(self.getSessionVar(self.user_data_key))
            print("ISLOGGED IN ---> {usr}")
            if usr['loggedIn'] == 'true' or usr['loggedIn'] == True :
                return True

        return False

    def getUserSession(self):
        usr = json.dumps(self.getSessionVar(self.user_data_key)).replace("\\","")
        print(f"jsondumps>>>>>>>>>>>>{usr}")
        try:
            usr = json.loads(usr[1:len(usr)-1])
            print(f"jsonLoads>>>>>>>>>>>>>>>>>{usr}")
            if usr['loggedIn'] == "true" or usr['loggedIn'] == True:
                usr['loggedIn'] = True
            else:
                usr['loggedIn'] = False
            return usr

        except Exception as e:
            cfg.debug("NO USER -----")
            return clearUserData()

    def getAppKey(self):
        return self.app_key


