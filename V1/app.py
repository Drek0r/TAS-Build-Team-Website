from flask import Flask, render_template, request, session, redirect, url_for

from V1.cfg import sec
from V1.cfg import cfg
from V1.cfg import user
from V1.cfg import db

import sqlite3
import datetime
import math
#pip install Flask-Session
from flask_session import Session
import json
from datetime import date
# pip install mcstatus
from mcstatus import MinecraftServer




# APP VARS

DEBUG = cfg.DEBUG

latestDoc = "https://1drv.ms/b/s!AqA1LpE9Eq3JgZYLsreleOySZs-stQ"
discordInvite ="https://discord.gg/PvWdYa2"


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
    sql = "SELECT subject, message, icon, date, id date from messages where type='alert' order by date desc"
    conn = create_connection(cfg.DB)
    cur = conn.cursor()
    results = cur.execute(sql).fetchall()
    for r in results:
        alert = {
            'subject': r[0],
            'txt': r[1],
            'icon': r[2],
            'date': r[3],
            'id': r[4]
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


def generateIconList():
    file = cfg.icon_list

    iconList = []
    f = open(file, "r")
    iList = f.readlines()
    f.close()

    for i in range(0, len(iList) - 1, 2):
        name = iList[i].strip()
        iconTxt = iList[i + 1].strip()
        line = (name, iconTxt)
        iconList.append(line)

    return iconList





app = Flask(__name__)
app.config.from_object('cfg')
sec = sec()
sess = Session()
# app.config['RESIZE_URL'] = 'http://127.0.0.1:500'
# app.config['RESIZE_ROOT'] = './static/assets/img/gallery/'
#
# resize = flask_resize.Resize(app)


@app.route('/')
@app.route('/logout')
@app.route('/dashboard')
def home():
    rule = request.url_rule

    sec.generateAppKeys()

    if 'logout' in rule.rule:
        sec.clearSession()
        user_data = user.clearUserData()
        sec.setSessionVar(sec.user_data_key, user_data)

    if sec.getSessionVar(sec.user_data_key) == False:
        user_data = user.clearUserData()
        sec.setSessionVar(sec.user_data_key, user_data)

    user_data = sec.getUserSession()


    cfg.debug(f">>>>>>USERDATA {user_data}",True)




    alerts = generateAlerts()
    server_data = getMCServerData()
    projects = getProjectData()
    return render_template(cfg.dashboard_page, title="Dashboard", a=alerts, u=user_data, s=server_data,p=projects)


@app.route('/login_page')
def login_page():
    if sec.isLoggedIn():
       pass
    else:
        return render_template(cfg.login_page)

@app.route('/login', methods=["POST"])
def loginAction():

    if sec.isLoggedIn():
        pass
    else:
        if request.method == "POST":
            email = request.form['email']
            password = request.form['password']

            data = (email, password)

            user_data= db.check_user(data)
            cfg.debug(user_data, True)

            sec.setSessionVar(sec.user_data_key,user_data)


    return redirect("/")


@app.route("/members")
def members_page():
    user_data= sec.getUserSession()
    memberList = db.getMemberList()
    alerts = generateAlerts()
    return render_template(cfg.members_page, title="Members List", u=user_data, ml=memberList, a=alerts)

@app.route("/gallery")
def pic_gallery():
    alerts = generateAlerts()
    user_data = sec.getUserSession()
    imageGallery = db.getImageDetails()
    cfg.debug(imageGallery,True)

    return render_template(cfg.gallery_page, title="Minecraft Gallery", u=user_data, i=imageGallery, a=alerts)

@app.route("/contact")
def contact():
    alerts = generateAlerts()
    user_data = sec.getUserSession()
    cfg.debug(f"Alerts: {alerts}", True)
    return render_template(cfg.contact_page, title="Contact us", u=user_data, a=alerts)


@app.route("/contact_action", methods=["POST"])
def contact_action():
    alerts = generateAlerts()
    user_data = sec.getUserSession()
    title = "Thank you for contacting us"
    message = {
        "heading": "Thank you",
        "message": "We will respond to your message shortly."
    }

    return render_template(cfg.contact_action_page, title=title, msg=message, u=user_data, a=alerts)


@app.route("/register")
def register():
    alerts = generateAlerts()
    user_data = sec.getUserSession()

    return render_template(cfg.register_page, title="Register", a=alerts, u=user_data)

@app.route("/terms")
def terms():
    return render_template(cfg.terms_page)


@app.route("/profile", methods=["POST"])
@app.route("/profile/<uid>", methods=["POST","GET"])
@app.route("/profile/update/", methods=["POST"])

def profile_page(uid=""):

    rule  = request.url_rule.rule


    user_data= sec.getUserSession()

    alerts = generateAlerts()
    if request.method == 'POST' and "update" in rule:

        # get formdata s
        cfg.debug("UPDATING PROFILE ",True)
        pwd = request.form['new_pwd']
        name = request.form['mcUsername']
        if request.form['orig_mc'] != name or pwd != "":
            sql = "UPDATE members set minecraftName = ? , pic = ?"
            if pwd.strip() != "":
                sql = sql + f", password = {pwd}"
            sql = sql + " where memberId = " + request.form['uid']

            pic = f"https://minotar.net/helm/{name}/50.png"

            data = (name, pic)

            cfg.debug(sql,True)
            cfg.debug(data,True)
            conn = create_connection(cfg.DB)
            cur = conn.cursor()
            cur.execute(sql,data)
            conn.commit()
            conn.close()

            user_data['mcUsername'] = name
            user_data['pic'] = pic

            sec.setSessionVar(sec.user_data_key,user_data)


        return render_template(cfg.profile_page, a=alerts, u=user_data)



    if uid == "" or user_data['loggedIn'] == False or uid != user_data['mcUsername']:
        cfg.debug(f"REDIRECTING FROM MEMBERS UPADTE uid: {uid} loggedIn: {user_data['loggedIn']} id: {user_data['id']}",True)
        return redirect("/")

    # display normal profile page

    return render_template(cfg.profile_page, a=alerts, u=user_data)

@app.route("/admin")
def admin_page():
    user_data = sec.getUserSession()
    if user_data['role'] not in cfg.ADMIN_ROLES or user_data['loggedIn'] == False:
        return redirect("/")

    alerts = generateAlerts()

    return render_template(cfg.admin_page, u=user_data, a=alerts)

### admin pages

'''
/alerts/edit
/server/update
/user/edit
/user/add
/gallery/edit
/meeting/edit
'''

@app.route("/alerts/", methods=["GET"])
@app.route("/alerts/edit/", methods=['POST'])
@app.route("/alerts/add", methods=["POST"])
def alerts():
    user_data = sec.getUserSession()
    alerts = generateAlerts()
    if request.method == "POST":
        rule = request.url_rule

        if "edit" in rule.rule:
            print("EDIT")


            alertIds = []
            for i in alerts:
                # print(i)
                alertIds.append(i['id'])

            for i in alertIds:
                '''
                alert_sub_1
                alert_sub_orig_1
                alert_txt_1
                alert_txt_orig_1
                '''

                txt_key = f'alert_txt_{i}'
                sub_key = f'alert_sub_{i}'
                orig_txt_key = f'alert_txt_orig_{i}'
                orig_sub_key = f'alert_sub_orig_{i}'
                del_key = f'alert_del_{i}'

                new_txt = request.form[txt_key]
                new_sub = request.form[sub_key]
                orig_txt = request.form[orig_txt_key]
                orig_sub = request.form[orig_sub_key]
                try:
                    delme = request.form[del_key]
                except KeyError as e:
                    delme = False

                if new_sub != orig_sub or new_txt != orig_txt or delme != False:
                    print(f"UPDATE {i}")
                    #print(f"{new_txt} | {orig_txt} | {new_sub} | {orig_sub} | >{delme}< |")
                    sql = ""
                    data = ()
                    if delme == "on":
                        sql = "DELETE FROM messages where id = ?"
                        data = (i,)
                    else:
                        sql = "UPDATE messages set 'subject' = ?, 'message' = ? where id = ?"
                        data = (new_sub, new_txt, i)

                    conn = create_connection(cfg.DB)
                    cur = conn.cursor()
                    cur.execute(sql,data)
                    conn.commit()

            return redirect("/alerts")


        # edit

        if "add" in rule.rule:
            # add
            alert_subject = request.form["new_alert_subject"]
            alert_txt = request.form["new_alert_txt"]
            icon = request.form["new_alert_icon"]

            now = date.today().strftime("%Y-%m-%d")
            sql = f"INSERT INTO MESSAGES ('type', 'from', 'subject', 'message', 'icon', 'date') "\
                    f"VALUES (?,?,?,?,?,?)"
            conn = create_connection(cfg.DB)
            cur = conn.cursor()
            data = ("alert", user_data['id'],alert_subject, alert_txt, icon, now)

            cur.execute(sql,data)
            conn.commit()
            return redirect("/alerts")

    else:
        user_data = sec.getUserSession()

        iconList = generateIconList()
        print(iconList)
        if sec.isLoggedIn():

            return render_template(cfg.adm_alerts_page, u=user_data,a=alerts, title="Admin - Alerts", icons=iconList)





@app.errorhandler(404)
@app.errorhandler(500)
def errorpage(error):
    alerts = generateAlerts()
    user_data = sec.getUserSession()
    errorMsg = "404"
    if "500" in f"{error}":
        errorMsg = "500"#

    return render_template('404.html', title="SOMETHING WENt WRONG - OUCH", errorshort=errorMsg, error=error, u=user_data, a=alerts)




if __name__ == "__main__":
    print("running")
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    sess.init_app(app)

app.debug = True
app.run()