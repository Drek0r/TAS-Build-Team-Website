from flask import Flask, render_template, request, session
from cfg import Config as cfg
from cfg import AppSecure as sec
from cfg import User as usr
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


def getMCServerData():
    cfg.debug(f"getMCServerData", DEBUG)
    # get mc server info
    mcServer = "minecraft.tas.qld.edu.au"
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

    sql = "SELECT MAX(maxPing), date from ping"
    cfg.debug(sql, DEBUG)
    conn = create_connection(cfg.DB)
    cur = conn.cursor()
    cur.execute(sql )
    maxPing = cur.fetchone()[0]


    if latency > maxPing:
        sql = f"INSERT INTO ping (maxPing, date) VALUES ({latency}, '{now}')"
        cfg.debug(sql , DEBUG)
        cur.execute(sql )
        conn.commit()
        maxPing = latency


    sql = "SELECT COUNT(name) FROM members"
    cur.execute(sql)
    count = cur.fetchone()[0]

    percent = math.floor(playersOnLine / playersMax * 100)

    # get avatar
    # tmpLst = []
    # for player in playersList:
    #
    #     sql = f"SELECT pic from members where minecraftName = '{player}'"
    #     cur.execute(sql)
    #     pic = cur.fetchone()[0]
    #
    #     cfg.debug(f"player: {player} {pic}")
    #     pName = player
    #     p = {"name": pName, "pic": pic}
    #     tmpLst.append(p)
    #
    # playersList = tmpLst



    # listOfPlayers = "THIS WILL BE A LIST OF ALL PLAYERS"
    serverData = {
        "ip": mcServer,
        "latency": latency,
        "playersList": playersList,
        "playerCount": playersOnLine,
        "playersMax": playersMax,
        "percent": percent,
        "maxPing": maxPing,
        "docLink": latestDoc,
        "discord": discordInvite,
        "members": count
    }
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

@app.route('/')
@app.route('/logout')
@app.route('/dashboard')
def home():
    server_data = getMCServerData()
    projects = getProjectData()
    return render_template('index.html', title="Dashboard", u=u.getUser(), s=server_data,p=projects)

@app.route('/login')
def loginpagefunction():
    return render_template(loginpage)

@app.errorhandler(404)
@app.errorhandler(500)
def errorpage(error):
    errorMsg = "404"
    if "500" in f"{error}":
        errorMsg = "500"#

    return render_template('404.html', title="SOMETHING WENt WRONG - OUCH", errorshort=errorMsg, error=error, u=u.getUser())


if __name__ == '__main__':
    app.run()
