from flask import Flask, render_template, request, session, redirect, url_for

from V1.cfg import sec
from V1.cfg import cfg
from V1.cfg import usr
from V1.cfg import db

import sqlite3
import datetime
import math
#pip install Flask-Session
from flask_session import Session

# pip install mcstatus
from mcstatus import MinecraftServer




# APP VARS

DEBUG = cfg.DEBUG

latestDoc = "https://1drv.ms/b/s!AqA1LpE9Eq3JgZYLsreleOySZs-stQ"
discordInvite ="https://discord.gg/PvWdYa2"

u = usr()
user_data = u.getUser()


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

def generateAlerts():

    alerts = []
    sql = "SELECT subject, message, icon, date from messages where type='alert' order by date desc"
    conn = create_connection(cfg.DB)
    cur = conn.cursor()
    results = cur.execute(sql).fetchall()
    for r in results:
        alert = {
            'subject': r[0],
            'txt': r[1],
            'icon': r[2],
            'date': r[3]
        }
        alerts.append(alert)

    return alerts

def getMCServerData():
    cfg.debug(f"getMCServerData", DEBUG)
    # get mc server info
    mcServer = "minecraft.tas.qld.edu.au"
    conn = create_connection(cfg.DB)
    sql = "SELECT MAX(maxPing), date from ping"
    cfg.debug(sql, DEBUG)

    cur = conn.cursor()
    cur.execute(sql)
    maxPing = cur.fetchone()[0]

    sql = "SELECT COUNT(name) FROM members"
    cur.execute(sql)
    count = cur.fetchone()[0]

    try:


        server = MinecraftServer(mcServer)
        status = server.status()

        latency = status.latency

        playersOnLine = status.players.online
        playersMax = status.players.max

        query = server.query()
        playersList = query.players.names
        cfg.debug(f"Playerlist: {playersList}", DEBUG)

        now = datetime.datetime.now()
        # get max ping from db.



        if latency > maxPing:
            sql = f"INSERT INTO ping (maxPing, date) VALUES ({status.latency}, '{now}')"
            cfg.debug(sql , DEBUG)
            cur.execute(sql )
            conn.commit()
            maxPing = f"{latency} ms"

        percent = math.floor(playersOnLine / playersMax * 100)

    except Exception as e:
        cfg.debug(f"MC error {e}", True)
        playersList = []
        playersOnLine = 0
        playersMax = 20
        percent = 0
        latency = "OFFLINE"
        count = 0


    # listOfPlayers = "THIS WILL BE A LIST OF ALL PLAYERS"
    serverData = {
        "ip": mcServer,
        "latency": f"{latency} ms",
        "playersList": playersList,
        "playerCount": playersOnLine,
        "playersMax": playersMax,
        "percent": percent,
        "maxPing": f"{maxPing} ms",
        "docLink": latestDoc,
        "discord": discordInvite,
        "members": count
    }
    cfg.debug(f"mc server data: {serverData} ", True)
    return serverData


def getProjectData():

    # todo change desc to be based on percent commplete
    sql = "SELECT name, percentComplete, desc from projectAreasTracking order by percentComplete ASC"
    conn = create_connection(cfg.DB)
    cur = conn.cursor()
    cur.execute(sql, )
    projectList = cur.fetchall()
    projects = []
    cfg.debug(projectList, DEBUG)
    for project in projectList:
        # if project[1] == 100:
        #     percent = "Completed"
        # else:
        style = project[2]
        percent =  f"{project[1] }%"
        p = { "name": project[0], "done": percent, 'style': style}
        projects.append(p)


    return projects



app = Flask(__name__)
app.config.from_object('cfg')
sec = sec()
sess = Session()



@app.route('/')
@app.route('/logout')
@app.route('/dashboard')
def home():
    rule = request.url_rule

    if 'logout' in rule.rule:
        sec.clearSession()
        u.user_data['loggedIn'] = False
        sec.setSessionVar(sec.user_data_key, u.user_data)


    alerts = generateAlerts()
    server_data = getMCServerData()
    projects = getProjectData()
    return render_template(cfg.dashboard_page, title="Dashboard", a=alerts, u=u.getUser(), s=server_data,p=projects)


@app.route('/login_page')
def login_page():
    return render_template(cfg.login_page)

@app.route('/login', methods=["POST"])
def memberpage():
    _user_data = sec.getSessionVar(sec.user_data_key)

    email = request.form['email']
    password = request.form['password']

    data = (email, password)

    user_exists = db.check_user(data)
    cfg.debug(user_exists, True)

    if user_exists:
        pic = f'https://minotar.net/helm/{user_exists[3]}/50.png" class="mcImage"'
        user_data['name'] = user_exists[0]
        user_data['id'] = user_exists[2]
        user_data['loggedIn'] = True
        user_data['avatar'] = pic #user_exists[5]
        user_data['email'] = user_exists[4]
        user_data['role'] = user_exists[6]

        #------ NOT DONE ---------------
    else:
        user_data['loggedIn'] = False

    return redirect("/")


@app.route("/members")
def members_page():
    memberList = db.getMemberList()
    return render_template(cfg.members_page, title="Members List", u=user_data, ml=memberList)

@app.errorhandler(404)
@app.errorhandler(500)
def errorpage(error):
    errorMsg = "404"
    if "500" in f"{error}":
        errorMsg = "500"#

    return render_template('404.html', title="SOMETHING WENt WRONG - OUCH", errorshort=errorMsg, error=error, u=u.getUser())





if __name__ == "__main__":
    print("running")
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    sess.init_app(app)

app.debug = True
app.run()