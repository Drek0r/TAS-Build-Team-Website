
class Config(object):

    def getAppKey(keyfile):
        # load the key
        file = open(keyfile, 'rb')
        key = file.read()
        file.close()
        return key

    def debug(msg, debug=False):
        if debug:
            print(f"debug: \t{msg}")


    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = 'do-i-really-need-this'
    KEY_FILE = "data/key.key"
    APP_KEY = getAppKey(KEY_FILE)
    FLASK_SECRET = SECRET_KEY
    DB = 'data/database.db'

    home_page = 'index.html'
    dashboard_page = "index.html"

    members_page = "table.html"
    error_page = "404.html"

    register_page = "/member/register.html"
    login_page = "/members/login.html"
    profile_page = "/members/profile.html"

    contact_page = "contact.html"
    terms_page = "terms.html"

    ## LEGACY TODO Clean up
    errorpagehtml = '404html'
    member_portal_page = 'index.html'
    registration_page = 'register.html'
    loginpage = 'login.html'
    profilepagehtml = 'profile.html'
    # members_page = 'table.html'
    registrationconfim_page = 'registrationcomplete.html'
    registrations = 'registrations.html'
    pageregistermember = 'register-1.html'
    member_registered_page = 'memberregistered.html'
    addloginpage = 'register-2.html'
    addedloginpage = 'registrationcomplete.html'
    accountinfopage = 'accountinfo.html'





