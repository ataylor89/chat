import os
import pickle
from datetime import datetime

class UserDao:
    def __init__(self):
        self.users = {}

    def load_user_db(self, path="users.pickle"):
        if os.path.exists(path):
            with open(path, "rb") as file:
                self.users.clear()
                self.users.update(pickle.load(file))

    def save_user_db(self, path="users.pickle"):
        with open(path, "w") as file:
            pickle.dump(self.users, file)

    def register(self, username, password):
        if username in self.users:
            return False
        self.users[username] = {"password": password, "registration_dt": datetime.now()}
        self.save_user_db()
        return True

    def attempt_login(self, username, password):
        return username in self.users and password == self.users[username]["password"]
