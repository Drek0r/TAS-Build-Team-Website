from flask import *
import sqlite3


#----------------------------------------
#--------- DataBase stuff ---------------
#----------------------------------------

database = "data/database.db"

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
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
    :param conn: connection to database 
    :param data: a tuple containing (username, password) 
    :return: true if user exists, false if they do not exist. 
    ''' 
 
    sql = "SELECT *  from users where  username=? and password=?" 
    conn = create_connection(database)

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
    conn = create_connection(database)

    with conn: 
        user_exists = check_user(conn,data) 
    if user_exists: 
        return render_template(member_portal_page, u=username)
    else: 
        #------ NOT DONE ---------------
        return render_template("something")
    
@app.route('/members')
def list_members():
    sql = "SELECT * FROM members"
    conn = create_connection(database)
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

@app.errorhandler(404)
def errorpage(error):
    return render_template('404.html')


app.run(debug=True)
