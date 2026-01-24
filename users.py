# The acronym DAO stands for "data access object"

# It's a paradigm that I often use when I write code that accesses a database

# In the previous iteration, I decided to make this module stateless
# But in this iteration, I changed my mind, and decided to make this module stateful

# What do the words state, stateful, and stateless mean?

# State refers to persistent data

# A module (or API) is stateful if it has persistent data
# A module (or API) is stateless if it does not have persistent data

# The word also gets used in object-oriented programming

# Objects are said to have state and behavior

# State refers to an object's data (which is persistent)
# Behavior refers to an object's methods

# In conclusion, we have defined the word "state" in two ways

# In a more general context, state refers to persistent data
# In the context of object-oriented programming, state refers to an object's data

# I wanted to write this brief introduction before we proceed with the code

import sha256
import os
import pickle
from user import User

class UserDatabase:
    def __init__(self):
        self.users = {}

    def load(self, path='users.pickle'):
        if os.path.exists(path):
            with open(path, 'rb') as file:
                self.users.clear()
                self.users.update(pickle.load(file))

    def save(self, path='users.pickle'):
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

    def attempt_login(self, username, password):
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
