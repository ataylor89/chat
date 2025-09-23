import packet_io
import packet_types
import socket
import threading
import pickle
import os
from datetime import datetime
from rsa import parser

host = "127.0.0.1"
port = 12345
clients = {}
users = {}
logged_in_users = []
rsa_keys = {}

def main():
    parse_keys()
    load_user_db()
    listen()

def listen():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    client_id = 0
    while True:
        client_socket, client_address = server_socket.accept()
        client_id += 1
        create_client(client_id, client_socket, client_address)
        thread = threading.Thread(target=readloop, args=(client_id,))
        thread.start()

def create_client(client_id, client_socket, client_address):
    clients[client_id] = {
        "client_name": format("Client-%d" %client_id),
        "client_socket": client_socket,
        "client_address": client_address,
        "public_key": None,
        "encryption": False
    }

def parse_keys():
    rsa_keys["public"] = parser.parse_key("rsa/publickey.txt")
    rsa_keys["private"] = parser.parse_key("rsa/privatekey.txt")

def load_user_db(path="users.pickle"):
    if os.path.exists(path):
        with open(path, "rb") as file:
            users.clear()
            users.update(pickle.load(file))

def save_user_db(path="users.pickle"):
    if len(users) > 0:
        with open(path, "wb") as file:
            pickle.dump(users, file)

def readloop(client_id):
    client = clients[client_id]
    client_socket = client["client_socket"]
    decryption_key = rsa_keys["private"]
    done = False
    while not done:
        try:
            use_encryption = client["encryption"]
            packet = packet_io.read_packet(client_socket, key=decryption_key, encryption=use_encryption)
            if packet:
                process(packet, client_id)
        except socket.error as e:
            print(e)
            client_socket.close()
            if "username" in client:
                logged_in_users.remove(client["username"])
            del clients[client_id]
            done = True

def process(packet, client_id):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    packet_type = packet[4]
    if packet_type == packet_types.EXCHANGE_PUBLIC_KEY:
        handle_exchange_public_key(packet, client_id)
    elif packet_type == packet_types.REGISTER:
        handle_registration(packet, client_id)
    elif packet_type == packet_types.LOGIN:
        handle_login(packet, client_id)
    elif packet_type == packet_types.MESSAGE:
        handle_message(packet, client_id)
    elif packet_type == packet_types.DATE:
        handle_date(packet, client_id)
    #elif packet_type == packet_types.DATETIME:
    #    handle_datetime(packet, client_id)
    elif packet_type == packet_types.TIME:
        handle_time(packet, client_id)

def handle_exchange_public_key(packet, client_id):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    client = clients[client_id]
    client_name = client["client_name"]
    client_socket = client["client_socket"]
    client_public_key = packet[5:packet_len].decode("utf-8")
    print("%s's public key is %s" %(client_name, client_public_key))
    client["public_key"] = parser.decode(client_public_key)
    server_public_key = parser.parse_key("rsa/publickey.txt")
    server_public_key_enc = parser.encode(server_public_key)
    print("The server's public key is %s" %server_public_key_enc)
    packet_io.write_packet(
        client_socket, 
        packet_types.EXCHANGE_PUBLIC_KEY, 
        server_public_key_enc, 
        key=client["public_key"], 
        encryption=client["encryption"])
    client["encryption"] = True

def handle_registration(packet, client_id):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    client = clients[client_id]
    client_socket = client["client_socket"]
    parts = packet[5:packet_len].decode("utf-8").split(":", 1)
    if len(parts) != 2:
        print("The registration packet from client %s does not meet the required format" %client["client_name"])
        message = "Server: The registration packet does not meet the required format\n"
        packet_io.write_packet(
            client_socket, 
            packet_types.REGISTER, 
            message, 
            key=client["public_key"], 
            encryption=client["encryption"])
        return
    username = parts[0]
    password = parts[1]
    if username in users:
        print("Unable to register username %s because it is already taken" %username)
        message = format("Server: The username %s is already taken\n" %username)
        packet_io.write_packet(
            client_socket, 
            packet_types.REGISTER, 
            message,
            key=client["public_key"],
            encryption=client["encryption"])
    else:
        users[username] = {"password": password, "registration_dt": datetime.now()}
        save_user_db()
        print("The username %s was successfully registered" %username)
        message = format("Server: The username %s was successfully registered\n" %username)
        packet_io.write_packet(
            client_socket, 
            packet_types.REGISTER, 
            message,
            key=client["public_key"],
            encryption=client["encryption"])

def handle_login(packet, client_id):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    client = clients[client_id]
    client_name = client["client_name"]
    client_socket = client["client_socket"]
    parts = packet[5:packet_len].decode("utf-8").split(":", 1)
    if len(parts) != 2:
        print("The login packet from %s does not meet the required format" %client_name)
        message = "Server: The login packet does not meet the required format\n"
        packet_io.write_packet(
            client_socket, 
            packet_types.LOGIN, 
            message,
            key=client["public_key"],
            encryption=client["encryption"])
        return
    username = parts[0]
    password = parts[1]
    if username in users and password == users[username]["password"] and username not in logged_in_users:
        client["username"] = username
        print("%s successfully logged in as %s" %(client_name, username))
        message = format("Server: Successfully logged in as %s\n" %username)
        packet_io.write_packet(
            client_socket, 
            packet_types.LOGIN, 
            message,
            key=client["public_key"],
            encryption=client["encryption"])
        logged_in_users.append(username)
    else:
        print("%s was unable to login" %client_name)
        message = "Server: Unable to login\n"
        packet_io.write_packet(
            client_socket, 
            packet_types.LOGIN, 
            message,
            key=client["public_key"],
            encryption=client["encryption"])
        return

def handle_message(packet, client_id):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    client = clients[client_id]
    username = client["username"] if "username" in client else client["client_name"]
    message = format("%s: %s" %(username, packet[5:packet_len].decode("utf-8")))
    print(message, end="")
    echo(message)

def echo(message):
    for client_id in clients:
        client = clients[client_id]
        client_socket = client["client_socket"]
        encryption_key = client["public_key"]
        use_encryption = client["encryption"]
        try:
            packet_io.write_packet(
                client_socket, 
                packet_types.MESSAGE, 
                message,
                key=encryption_key,
                encryption=use_encryption)
        except socket.error as e:
            print(e)

def handle_date(packet, client_id):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    client = clients[client_id]
    client_socket = client["client_socket"]
    encryption_key = client["public_key"]
    use_encryption = client["encryption"]
    if packet_len == 5:
        today = datetime.now()
        message = format("Server: The date is %s\n" %today.strftime("%A, %B %-d, %Y"))
        try:
            packet_io.write_packet(
                client_socket,
                packet_types.DATE,
                message,
                key=encryption_key,
                encryption=use_encryption)
        except socket.error as e:
            print(e)

def handle_time(packet, client_id):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    client = clients[client_id]
    client_socket = client["client_socket"]
    encryption_key = client["public_key"]
    use_encryption = client["encryption"]
    if packet_len == 5:
        now = datetime.now().astimezone()
        message = format("Server: The time is %s\n" %now.strftime("%-I:%M %p %Z"))
        try:
            packet_io.write_packet(
                client_socket,
                packet_types.TIME,
                message,
                key=encryption_key,
                encryption=use_encryption)
        except socket.error as e:
            print(e)

if __name__ == "__main__":
    main()
