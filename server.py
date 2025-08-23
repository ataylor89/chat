# This is a work in progress

import packet_types
import socket
import threading
import pickle
import os
from datetime import datetime

clients = {}
users = {}

def main():
    load_user_db()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = '127.0.0.1'
    port = 12345
    server_socket.bind((host, port))

    server_socket.listen()
    i = 0

    while True:
        client_socket, client_address = server_socket.accept()
        i += 1
        client_name = format("Client-%d" %i)
        clients[client_name] = (client_socket, client_address)
        thread = threading.Thread(target=readloop, args=(client_socket,client_name))
        thread.start()

def load_user_db(path="users.pickle"):
    if os.path.exists(path):
        with open(path, "rb") as file:
            users.clear()
            users.update(pickle.load(file))

def save_user_db(path="users.pickle"):
    if len(users) > 0:
        with open(path, "wb") as file:
            pickle.dump(users, file)

def readloop(client_socket, client_name):
    done = False
    while not done:
        try:
            data = client_socket.recv(4)
            if len(data) < 4:
                continue
            packet_len = int.from_bytes(data, byteorder="big", signed=False)
            packet = data + client_socket.recv(packet_len-4)
            if len(packet) == packet_len:
                process(packet, client_name)
            else:
                print("The packet is shorter than the specified length")
        except socket.error as e:
            print(e)
            client_socket.close()
            del clients[clientname]
            done = True

def process(packet, client_name):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    packet_type = packet[4]
    if packet_type == packet_types.REGISTER:
        handle_registration(packet, client_name)
    elif packet_type == packet_types.MESSAGE:
        handle_message(packet, client_name)

def handle_registration(packet, client_name):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    client_socket, client_address = clients[client_name]
    parts = packet[5:packet_len].decode("utf-8").split(":", 1)
    if len(parts) != 2:
        client_socket.sendall("Message from server: The registration packet does not meet the required format".encode("utf-8"))
        return
    username = parts[0]
    password = parts[1]
    if username in users:
        print("Unable to register username %s because it is already taken" %username)
        client_socket.sendall("Message from server: The username is already taken".encode("utf-8"))
    else:
        users[username] = {"username": username, "password": password, "registration_dt": datetime.now()}
        save_user_db()
        message = format("Message from server: The username %s was successfully registered" %username)
        print("The username %s was successfully registered" %username)
        client_socket.sendall(message.encode("utf-8"))

def handle_message(packet, client_name):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    message = format("%s: %s" %(client_name, packet[5:packet_len].decode("utf-8")))
    print(message)
    echo(message)

def echo(message):
    for client_name in clients:
        client_socket, client_address = clients[client_name]
        try:
            client_socket.sendall(message.encode("utf-8"))
        except socket.error as e:
            print(e)

if __name__ == "__main__":
    main()
