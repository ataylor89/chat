from server import project_root
from server.user import User
from shared import sha256
import os
import pickle

class UserManager:

    def __init__(self):
        self.users = {}

    def load(self):
        path = project_root / 'database' / 'users.pickle'
        if os.path.exists(path):
            with open(path, 'rb') as file:
                self.users.clear()
                self.users.update(pickle.load(file))

    def save(self):
        path = project_root / 'database' / 'users.pickle'
        with open(path, 'wb') as file:
            pickle.dump(self.users, file)

    def register(self, username, password):
        if username in self.users:
            return False
        salt = os.urandom(16)
        salted_password = salt + password.encode('utf-8')
        password_hash = sha256.sha256(salted_password).hexdigest
        self.users[username] = User(username, salt, password_hash)
        self.save()
        return True

    def login(self, username, password):
        if username not in self.users or self.users[username].logged_in:
            return False
        user = self.users[username]
        salted_password = user.salt + password.encode('utf-8')
        password_hash = sha256.sha256(salted_password).hexdigest
        if password_hash == user.password_hash:
            user.logged_in = True
            return True

    def logout(self, username):
        if username in self.users:
            self.users[username].logged_in = False
