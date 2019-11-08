

class User:

    def __init__(self):

        self.user_data = {
            "name": "",
            "id": "",
            "role": "guest",
            "key": "",
            "loggedIn": False,
            "avatar": "default.png",
            "email": ""
        }

    def getUser(self):
        return self.user_data