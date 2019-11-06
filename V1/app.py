from flask import Flask, render_template, request, session
from flask_session import Session
from cryptography.fernet import Fernet
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from uuid import uuid4
import sqlite3
from flask_bcrypt  import Bcrypt

# cryptography stuff from https://nitratine.net/blog/post/encryption-and-decryption-in-python/
# session stuff : https://pythonhosted.org/Flask-Session/

#----------------------------------------
#--------- DATABASE stuff ---------------
#----------------------------------------
app = Flask(__name__)
sess = Session()
DATABASE = "data/database.db"
DEBUG = True

KEY = "data/key.key"

#----------------------------------------
#--------- ALL Pages --------------------
#----------------------------------------
homepage = 'blank.html'
errorpagehtml = '404html'
member_portal_page = 'index.html'
registration_page = 'register.html'
loginpage = 'login.html'
profilepagehtml = 'profile.html'
members_page = 'table.html'
registrationconfim_page = 'registrationcomplete.html'
registrations = 'registrations.html'
pageregistermember = 'register-1.html'
member_registered_page = 'memberregistered.html'
addloginpage = 'register-2.html'
addedloginpage = 'registrationcomplete.html'
accountinfopage = 'accountinfo.html'

def getAppKey():
    # load the key
    file = open(KEY, 'rb')
    key = file.read()
    file.close()
    return key

    # key = getAppKey()

def debug(msg):
    if DEBUG:
        print(f"debug: \t{msg}")

def create_connection(db_file):
    """ create a DATABASE connection to the SQLite DATABASE
        specified by db_file
    :param db_file: DATABASE file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)
 
    return conn

def check_user(data):
    '''
    :param data: a tuple containing (username, password)
    :return: true if user exists, false if they do not exist. 
    '''
    conn = create_connection(DATABASE)

    sql = "SELECT *  from users where  username=? and password=?"
    debug(sql)
    debug(data)
    cur = conn.cursor() 

    cur.execute(sql,data)

    user = cur.fetchone()

    conn.close()

    if user:
        return user 
    else:
        return "USER NOT FOUND" 




def hashTxt(txt):
    hash = Bcrypt.bcrypt.generate_password_hash(txt)
    return hash

def compTxtWithHash(txt, hash):
    txtHash = Bcrypt.bcrypt.generate_password_hash(txt)
    if txtHash == hash:
        return True
    return False


# alerts

def generateAlerts():

    alerts = []
    alerts.append(
        {'txt':"A new monthly report is ready to download!" ,
         'icon': 'fa-file-alt'
         })
    alerts.append(
        {'txt': "Server is operating with no issues",
         'icon': 'fa-exchange-alt'
         })
    alerts.append(
        {'txt': "Openings are limited",
         'icon': 'fa-exclamation-triangle'
         })
    alerts.append(
        {'txt': "THis is another alert",
         'icon': 'fa-exclamation-triangle'
         })


    return alerts

def decryptTxt(encTxt, encKey=None):
    _key = encKey
    _txt = encTxt

    if _key==None:
        _key = getAppKey()

    if not isinstance(_key, bytes):
        _key = _key.encode()

    f = Fernet(_key)
    decTxt = f.decrypt(_key)
    return decTxt

def encTxt(pTxt, encKey=None):
    _key = encKey
    _txt = pTxt

    if _key == None:
        _key = getAppKey()
    if not isinstance(_key, bytes):
        _key = _key.encode()
    if not isinstance(_txt, bytes):
        _txt = _txt.encode()

    f = Fernet(_key)
    # encode converts to bytes
    encTxt = f.encrypt(_txt)

    return encTxt

def genUserKey(pwd="thisisadefalultValueThatSHouldBeChAnged"):
    # This is input in the form of a string
    password = pwd.encode()  # Convert to type bytes
    salt = uuid4().bytes  # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    userKey = base64.urlsafe_b64encode(kdf.derive(password))
   # base64.decode(cipher_suite.decrypt(token, encoding="ascii")

    return userKey

def getUserKey(pwd,appKey=False):
    if appKey:
        return getAppKey()
    else:
        if not session['userKey']:

            session['userKey'] = genUserKey(pwd)

        return session['userKey']

def setEncSessionVar(decVarName, decValue):
    sessionKey = getSessionKey()
    encVar = encTxt(decVarName,sessionKey).decode()
    encValue = encTxt(decValue, sessionKey).decode()

    session[encVar] = encValue

def getSessionVar(decVarName):
    sessoinKey = getSessionKey()
    sessionKey = base64.urlsafe_b64decode(sessoinKey)
    encVarName = encTxt(decVarName,sessoinKey).decode()
    encVar = session.get(encVarName)
    decVar = decryptTxt(encVar,sessoinKey)

    return decVar

def getSessionKey():
    encSessionKeyName = encTxt('sessionKey').decode()
    if not session.get(encSessionKeyName):
        session[encSessionKeyName] = genUserKey()

    return session[encSessionKeyName]




# def checkUserHasRole(encUserId,encRoleName):
#     encKey = getUserKey()
#
#     if session.get('userKey'):
#         pass
#
#     userId = decryptTxt(encUserId,)
#
#
#
#     sql = f"SELECT m.memberID  from members m " \
#         f"join roles r on m.roleID = r.roleID " \
#         f"WHERE m.memberID = {userId} AND r.roleName = {roleName}"
#

#----------------------------------------
#--------- Actual Page Code -------------
#----------------------------------------
@app.route('/')
def root():
    alerts =  generateAlerts()
    # set session key
    sessionKey = getSessionKey()
    print(sessionKey)
    # test setting session var
    setEncSessionVar("Test1","This is a test")
    test1 = getSessionVar("Test1")

    print(test1)

    return render_template(homepage, alerts=alerts)

@app.route('/login')
def loginpagefunction():
    return render_template(loginpage)

@app.route('/logout')
def logoutpage():
    return render_template(homepage)

@app.route('/memberportal', methods=["POST"])
def memberpage():
    username = request.form['username']
    password = request.form['password']

    data = (username, password)

    user_exists = check_user(data)

    if user_exists:
        user = user_exists
        print(user)
        return render_template(member_portal_page, user=user)
    else: 
        #------ NOT DONE ---------------
        return render_template("/", meg="Please Try Again")

@app.route('/member_portal')
def memberportalpage():
    return render_template(member_portal_page)

@app.route('/members')
def list_members():
    sql = "SELECT * FROM members"
    conn = create_connection(DATABASE)
    cur = conn.cursor()
    cur.execute(sql,)
    memberlist = cur.fetchall()
    return render_template(members_page, m=memberlist)

@app.route('/profile')
def profilepage():
    return render_template(profilepagehtml)

@app.route('/register')
def registration():
    return render_template(registration_page)

@app.route('/registrations')
def registrationslist():
    sql = "SELECT * FROM rego"
    conn = create_connection(DATABASE)

    cur = conn.cursor()
    cur.execute(sql,)
    members = cur.fetchall()
    return render_template(registrations, m=members)

@app.route('/registrationconfirmation', methods=['POST'])
def registrationconfim():
    name = request.form['name']
    position = request.form['Position']
    email = request.form['email']
    mc_username = request.form['password']
    conn = create_connection(DATABASE)

    data = (name, position, email, mc_username)

    sql = "INSERT INTO rego (name, position, email, mc_username) VALUES (?,?,?,?)"

    cur = conn.cursor()
    cur.execute(sql,data)
    conn.commit()
    conn.close()

    return render_template(registrationconfim_page)


@app.route('/registermember')
def registermemberpage():
    return render_template(pageregistermember)

@app.route('/memberregistered', methods=['POST'])
def memberregisteredwebpage():
    name = request.form['name']
    position = request.form['position']
    grade = request.form['Grade']
    mcname = request.form['mcname']
    date = request.form['date']
    areas = request.form['areas']
    email = request.form['email']

    conn = create_connection(DATABASE)
    cur = conn.cursor()
    data = (name, position, grade, mcname, date, email, areas)
    sql = "INSERT INTO members (Name, Position, Grade, MCName, StartDate, Email, areas) VALUES (?,?,?,?,?,?,?)"

    cur.execute(sql,data)
    conn.commit()
    conn.close()

    return render_template(member_registered_page)


@app.route('/loginadd')
def addinglogin():
    return render_template(addloginpage)

@app.route('/addedlogin', methods=['POST'])
def addedlogin():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    sql = "INSERT INTO users (username, password, email) VALUES (?,?,?)"
    data = (name, email, password)

    conn = create_connection(DATABASE)
    cur = conn.cursor()
    cur.execute(sql,data)

    conn.commit()
    conn.close()

    return render_template(addedloginpage)

@app.route('/accountinfo')
def accountinformation():
    sql = "SELECT * FROM users"
    conn = create_connection(DATABASE)
    cur = conn.cursor()
    cur.execute(sql,)

    info = cur.fetchall()

    return render_template(accountinfopage, i=info)

@app.errorhandler(404)
def errorpage(error):
    return render_template('404.html')

if __name__ == "__main__":
    print("running")

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'redis'

    sess.init_app(app)

    app.debug = True
    app.run()