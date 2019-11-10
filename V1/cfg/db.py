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

    sql =   "SELECT m.name, m.username, m.memberId, m.minecraftName, m.email, m.pic,  m.areas, m.firstname, m.lastname, r.roleName, p.positionName ,g.name as grade "\
            "FROM members m join gradeLevel g on m.grade = g.gradeLevelID JOIN positions p on m.position = p.positionID"\
            " JOIN roles r on r.roleID = m.roleId where  m.email=? and m.password=?"\
            " ORDER BY grade DESC"

    # name 0, username 1, id 2, mcname 3, email 4, pic 5, aras 6, fnanme 7, lname 8, role 9, position 10, grade 11

    # sql = "SELECT m.name, m.username, m.memberId, m.minecraftName, m.email, m.pic, r.roleName " \
    #       " from members m join roles r where  m.email=? and m.password=?"

    cfg.debug(sql, True)
    cfg.debug(data, True)
    cur = conn.cursor()

    cur.execute(sql, data)

    user = cur.fetchone()
    cfg.debug(user)

    conn.close()
    user_data = {}
    if user:
        # name 0, username 1, id 2, mcname 3, email 4, pic 5, aras 6, role 7, position 8, grade 9
        pic = f'https://minotar.net/helm/{user[3]}/50.png'
        user_data['loggedIn'] = True
        user_data['name'] = user[0]
        user_data['id'] = user[2]
        user_data['mcUsername'] = user[3]
        user_data['email'] = user[4]
        user_data['avatar'] = pic  # user_exists[5]
        user_data['areas'] = user[6]
        user_data['firstname'] = user[7]
        user_data['lastname'] = user[8]
        user_data['role'] = user[9]
        user_data['position'] = user[10]
        user_data['grade'] = user[11]

            # ------ NOT DONE ---------------
    else:
        user_data['id'] = 0
        user_data['avatar'] = "default"
        user_data['role'] = "Guest"
        user_data['loggedIn'] = False

    return user_data



def getMemberList():
    # sql = "SELECT * FROM members"
    sql = "SELECT m.name, p.positionName ,g.name as grade, m.minecraftName, m.email, m.areas,  m.pic  "\
            "FROM members m join gradeLevel g on m.grade = g.gradeLevelID JOIN positions p on m.position = p.positionID"\
            " ORDER BY grade DESC"
    conn = create_connection(cfg.DB)
    cur = conn.cursor()
    cur.execute(sql, )
    memberList = cur.fetchall()
    cfg.debug(f"MEMBERS: sql - {sql} MList: {memberList}",True)


    


    return memberList


def getImageDetails():
    sql = "SELECT imageName, imageAlt, imageDesc from gallery"
    conn = create_connection(cfg.DB)
    cur = conn.cursor()
    cur.execute(sql, )
    imageList = cur.fetchall()

    images = []
    for image in imageList:
        i = {
            "img": image[0],
            "alt": image[1],
            "desc": image[2]
              }
        images.append(i)

    return images
