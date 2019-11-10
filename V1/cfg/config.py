from datetime import datetime

class Config(object):

    def getAppKey(keyfile):
        # load the key
        file = open(keyfile, 'rb')
        key = file.read()
        file.close()
        return key

    def debug(msg, debug=False):
        DEBUG = True
        if debug and DEBUG:
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            ts = datetime.fromtimestamp(timestamp)

            print(f"debug: {ts} \t{msg}")


    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = 'do-i-really-need-this'
    KEY_FILE = "data/key.key"
    APP_KEY = getAppKey(KEY_FILE)
    FLASK_SECRET = SECRET_KEY
    DB = 'data/database.db'
    ADMIN_ROLES = ['Admin']
    icon_list = "data/fa-icon-list.txt"

    home_page = 'index.html'
    dashboard_page = "index.html"

    members_page = "table.html"
    error_page = "404.html"

    message_page = "messagePage.html"

    register_page = "members/register.html"
    login_page = "members/login.html"
    profile_page = "members/profile.html"
    forgot_pwd_page ="members/forgot-password.html"
    gallery_page = "gallery.html"
    contact_page = "contact.html"
    contact_action_page = message_page
    terms_page = "terms.html"
    admin_page = "admin.html"


    '''
   /alerts/edit
    /server/update
    /user/edit
    /user/add
    /gallery/edit
    /meeting/edit
    '''

    adm_alerts_page = "alerts.html"
    adm_alerts_edit = message_page
    adm_alerts_add = message_page

    ## LEGACY TODO Clean up
    #errorpagehtml = '404html'
    member_portal_page = 'index.html'
    registration_page = 'register.html'
    #loginpage = 'login.html'
    profilepagehtml = 'profile.html'
    # members_page = 'table.html'
    registrationconfim_page = 'registrationcomplete.html'
    registrations = 'registrations.html'
    pageregistermember = 'register-1.html'
    member_registered_page = 'memberregistered.html'
    addloginpage = 'register-2.html'
    addedloginpage = 'registrationcomplete.html'
    accountinfopage = 'accountinfo.html'





