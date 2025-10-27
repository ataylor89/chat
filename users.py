# This is a stateless API to the user database

# When an API is stateful, it often makes sense to use classes and objects
# When an API is stateless, it is sometimes not necessary to use classes and objects

# It is worth asking, "What do we mean by state, stateful, and stateless?"

# It is often said that objects have state and behavior
# State is a reference to an object's data
# Behavior is a reference to an object's methods

# In the context of object-oriented programming, state refers to an object's data
# In a more general context, state refers to persistent data

# We can use global variables to save a program's state, but this runs into many difficulties
# It is often more elegant, more practical, more organized, and more convenient, to use an object to store state

# The packet_io module has state (i.e. the logger, its path, and its mode) so we encapsulate this state inside an object
# This module, on the other hand, is stateless, so we don't need a class or object

# There are many advantages to making this module stateless
# One advantage is that it saves memory (a large, persistent, in-memory user database would end up using a lot of memory)

# I wanted to have a brief discussion about stateful versus stateless APIs, before I proceed with the code

import os
import pickle
from datetime import datetime

def get_users():
    if os.path.exists("users.pickle"):
        with open("users.pickle", "rb") as file:
            return pickle.load(file)
    return {}

def register(username, password):
    users = get_users()
    if username in users:
        return False
    users[username] = {"password": password, "registration_dt": datetime.now()}
    with open("users.pickle", "wb") as file:
        pickle.dump(users, file)
    return True

def attempt_login(username, password):
    users = get_users()
    return username in users and password == users[username]["password"]
