from datetime import datetime

class User:
    def __init__(self, username, salt, password_hash):
        self.username = username
        self.salt = salt
        self.password_hash = password_hash
        self.registration_dt = datetime.now()
        self.logged_in = False

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['logged_in']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.logged_in = False
