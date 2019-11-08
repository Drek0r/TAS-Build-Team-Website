from cryptography.fernet import Fernet
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from uuid import uuid4
import argparse
import random
KEY = "../V1/data/key.key"

def genPwd():
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    pw_length = 8
    mypw = ""

    for i in range(pw_length):
        next_index = random.randrange(len(alphabet))
        mypw = mypw + alphabet[next_index]

    mypw.replace("o","0")
    mypw.replace("i","1")
    mypw.replace("e","3")
    mypw.replace("g","9")

    return mypw

def genUserKey(pwd):
    _pwd = pwd
    if _pwd == None:
        _pwd = genPwd()
    # This is input in the form of a string
    _pwd = _pwd.encode()  # Convert to type bytes
    salt = uuid4().bytes  # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    userKey = base64.urlsafe_b64encode(kdf.derive(_pwd))

    return userKey, _pwd

def getAppKey():
    # load the key
    file = open(KEY, 'rb')
    key = file.read()
    file.close()
    return key


def encTxt(pwd, key):
    f = Fernet(key)
    # encode converts to bytes
    encTxt = f.encrypt(pwd.encode())

    return encTxt


def decryptTxt(encTxt, encKey=None):
    _key = encKey
    _txt = encTxt
    if _key == None:
        _key = getAppKey()

    if not isinstance(_key, bytes):
        _key = _key.encode()

    _txt = encTxt.encode()
    print(_txt, _key)

    f = Fernet(_key)
    decTxt = f.decrypt(_txt)
    return decTxt


parser = argparse.ArgumentParser(description='some command line utilis for Tas Build Team')
parser.add_argument("--k", default=None, help="key")
parser.add_argument("--p", default=None, help="pwd to enc")
parser.add_argument("--d", default=None, help="text to decrypt")
parser.add_argument("--g", default=None, help="Generate User Key and PWD")

args = parser.parse_args()

key = args.k
pwd = args.p
dec = args.d
gen = args.g

if gen is not None:
    print(f"Generating User Key from pwd {pwd}")

    userKey,pwd = genUserKey(pwd)

    print("*"*5)
    print(f"key: {userKey.decode()}")
    print(f"pwd: {pwd}")
    print("*"*5)

if dec is not None:
    print(f"Decrypt: {dec}")
    if key is None:
        key = getAppKey()

    decTxt = decryptTxt(dec, key)
    print("*" * 5)
    print(f"key: {key.decode()}")
    print(f"pwd: {dec.decode()}")
    print("*" * 5)

# if key == None:
#     key = getAppKey()
#
# if pwd == None:
#     pwd = genPwd()
#
# encPwd = encTxt(pwd,key)
# decTxtPwd = decryptTxt(encPwd,key)
# print(f"{pwd} : {encPwd}")
# print(f"{encPwd}: {decTxtPwd}")
#
