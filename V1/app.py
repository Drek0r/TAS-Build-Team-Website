from flask import *
import sqlite3


#----------------------------------------
#--------- DATABASE stuff ---------------
#----------------------------------------

DATABASE = "data/database.db"

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

def check_user(conn, data): 
    '''
    :param conn: connection to DATABASE 
    :param data: a tuple containing (username, password) 
    :return: true if user exists, false if they do not exist. 
    ''' 
 
    sql = "SELECT *  from users where  username=? and password=?" 
    conn = create_connection(DATABASE)

    cur = conn.cursor() 
    cur.execute(sql,data) 
    user = cur.fetchone() 
    if user: 
        return user 
    else:
        return "USER NOT FOUND" 



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

app = Flask(__name__)

#----------------------------------------
#--------- Actual Page Code -------------
#----------------------------------------
@app.route('/')
def root():
    return render_template(homepage)

@app.route('/login')
def loginpagefunction():
    return render_template(loginpage)

@app.route('/memberportal', methods=["POST"])
def memberpage():
    username = request.form['username']
    password = request.form['password']
    data = (username, password)
    user_exists = False
    conn = create_connection(DATABASE)

    with conn: 
        user_exists = check_user(conn,data) 
    if user_exists: 
        return render_template(member_portal_page, u=username)
    else: 
        #------ NOT DONE ---------------
        return render_template("something")

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


app.run(debug=True)
