import sqlite3
from .config import Config as cfg


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


def getMemberList():
    # sql = "SELECT * FROM members"
    sql = "SELECT m.name, p.positionName , m.minecraftName, m.email, m.areas, g.name as grade " \
          "FROM members m join gradeLevel g on m.grade = g.gradeLevelID JOIN positions p on m.position = p.positionID" \
          " ORDER BY grade DESC"
    conn = create_connection(cfg.DB)
    cur = conn.cursor()
    cur.execute(sql, )
    memberList = cur.fetchall()

    return memberList


def getProjectData():
    sql = "SELECT name, percentComplete from projectAreasTracking"
    conn = create_connection(cfg.DB)
    cur = conn.cursor()
    cur.execute(sql, )
    projectList = cur.fetchall()
    projects = []
    cfg.debug(projectList)
    for project in projectList:
        # if project[1] == 100:
        #     percent = "Completed"
        # else:
        percent = f"{project[1]}%"
        p = {"name": project[0], "done": percent}
        projects.append(p)

    return projects


def check_user(data):
    '''
    :param data: a tuple containing (username, password)
    :return: true if user exists, false if they do not exist.
    '''
    conn = create_connection(cfg.DB)

    sql = "SELECT m.name, m.username, m.memberId, m.minecraftName, m.email, m.pic, r.roleName " \
          " from members m join roles r where  m.email=? and m.password=?"

    cfg.debug(sql, True)
    cfg.debug(data, True)
    cur = conn.cursor()

    cur.execute(sql, data)

    user = cur.fetchone()
    cfg.debug(user)

    conn.close()

    if user:
        return user
    else:
        return "USER NOT FOUND"

