from packet_io import PacketIO
import packet_types
import socket
import threading
import pickle
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from rsa import parser
import configparser

class Application:
    def __init__(self, config, packetIO):
        self.host = config["default"]["host"]
        self.port = int(config["default"]["port"])
        self.clients = {}
        self.users = {}
        self.logged_in_users = []
        self.rsa_keys = {}
        self.packetIO = packetIO

    def listen(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        client_id = 0
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_id += 1
            self.create_client(client_id, client_socket, client_address)
            thread = threading.Thread(target=self.readloop, args=(client_id,))
            thread.start()

    def create_client(self, client_id, client_socket, client_address):
        self.clients[client_id] = {
            "client_name": format("Client-%d" %client_id),
            "client_socket": client_socket,
            "client_address": client_address,
            "public_key": None,
            "encryption": False,
            "logged_in": False,
            "username": None
        }

    def parse_keys(self):
        self.rsa_keys["public"] = parser.parse_key("rsa/publickey.txt")
        self.rsa_keys["private"] = parser.parse_key("rsa/privatekey.txt")

    def load_user_db(self, path="users.pickle"):
        if os.path.exists(path):
            with open(path, "rb") as file:
                self.users.clear()
                self.users.update(pickle.load(file))

    def save_user_db(self, path="users.pickle"):
        if len(self.users) > 0:
            with open(path, "wb") as file:
                pickle.dump(self.users, file)

    def readloop(self, client_id):
        client = self.clients[client_id]
        client_socket = client["client_socket"]
        decryption_key = self.rsa_keys["private"]
        done = False
        while not done:
            try:
                use_encryption = client["encryption"]
                packet = self.packetIO.read_packet(client_socket, key=decryption_key, encryption=use_encryption)
                if packet:
                    self.process(packet, client_id)
            except socket.error as e:
                print(e)
                client_socket.close()
                if client["logged_in"]:
                    self.logged_in_users.remove(client["username"])
                del self.clients[client_id]
                done = True
            except Exception as e:
                print(e)

    def process(self, packet, client_id):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        packet_type = packet[4]
        if packet_type == packet_types.EXCHANGE_PUBLIC_KEY:
            self.handle_exchange_public_key(packet, client_id)
        elif packet_type == packet_types.REGISTER:
            self.handle_registration(packet, client_id)
        elif packet_type == packet_types.LOGIN:
            self.handle_login(packet, client_id)
        elif packet_type == packet_types.LOGOUT:
            self.handle_logout(packet, client_id)
        elif packet_type == packet_types.MESSAGE:
            self.handle_message(packet, client_id)
        elif packet_type == packet_types.DATE:
            self.handle_date(packet, client_id)
        elif packet_type == packet_types.TIME:
            self.handle_time(packet, client_id)

    def handle_exchange_public_key(self, packet, client_id):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        client = self.clients[client_id]
        client_name = client["client_name"]
        client_socket = client["client_socket"]
        client_public_key_enc = packet[5:packet_len].decode("utf-8")
        client["public_key"] = parser.decode(client_public_key_enc)
        server_public_key = parser.parse_key("rsa/publickey.txt")
        server_public_key_enc = parser.encode(server_public_key)
        encryption_key = client["public_key"]
        use_encryption = client["encryption"]
        self.packetIO.write_packet(
            client_socket, 
            packet_types.EXCHANGE_PUBLIC_KEY, 
            server_public_key_enc, 
            key=encryption_key, 
            encryption=use_encryption)
        client["encryption"] = True
        print("%s's public key is %s" %(client_name, client_public_key_enc))
        print("The server's public key is %s" %server_public_key_enc)

    def handle_registration(self, packet, client_id):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        client = self.clients[client_id]
        client_socket = client["client_socket"]
        encryption_key = client["public_key"]
        use_encryption = client["encryption"]
        tokens = packet[5:packet_len].decode("utf-8").split(":", 1)
        username = tokens[0]
        password = tokens[1]
        if username in self.users:
            print("Unable to register username %s because it is already taken" %username)
            message = format("Server: The username %s is already taken\n" %username)
            self.packetIO.write_packet(
                client_socket, 
                packet_types.REGISTER, 
                message,
                key=encryption_key,
                encryption=use_encryption)
        else:
            self.users[username] = {"password": password, "registration_dt": datetime.now()}
            self.save_user_db()
            print("The username %s was successfully registered" %username)
            message = format("Server: The username %s was successfully registered\n" %username)
            self.packetIO.write_packet(
                client_socket, 
                packet_types.REGISTER, 
                message,
                key=encryption_key,
                encryption=use_encryption)

    def handle_login(self, packet, client_id):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        client = self.clients[client_id]
        client_name = client["client_name"]
        client_socket = client["client_socket"]
        encryption_key = client["public_key"]
        use_encryption = client["encryption"]
        tokens = packet[5:packet_len].decode("utf-8").split(":", 1)
        username = tokens[0]
        password = tokens[1]
        if username in self.users and password == self.users[username]["password"] and username not in self.logged_in_users:
            client["username"] = username
            client["logged_in"] = True
            print("%s successfully logged in as %s" %(client_name, username))
            message = format("Server: Successfully logged in as %s\n" %username)
            self.packetIO.write_packet(
                client_socket, 
                packet_types.LOGIN, 
                message,
                key=encryption_key,
                encryption=use_encryption)
            self.logged_in_users.append(username)
        else:
            print("%s was unable to login" %client_name)
            message = format("Server: Unable to login as %s\n" %username)
            self.packetIO.write_packet(
                client_socket, 
                packet_types.LOGIN, 
                message,
                key=encryption_key,
                encryption=use_encryption)

    def handle_logout(self, packet, client_id):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        client = self.clients[client_id]
        client_name = client["client_name"]
        client_socket = client["client_socket"]
        encryption_key = client["public_key"]
        use_encryption = client["encryption"]
        username = client["username"]
        if client["logged_in"]:
            client["username"] = None
            client["logged_in"] = False
            message = format("Server: Successfully logged out of the account %s\n" %username)
            self.packetIO.write_packet(
                client_socket,
                packet_types.LOGOUT,
                message,
                key=encryption_key,
                encryption=use_encryption)

    def handle_message(self, packet, client_id):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        client = self.clients[client_id]
        username = client["username"] if client["logged_in"] else client["client_name"]
        message = format("%s: %s" %(username, packet[5:packet_len].decode("utf-8")))
        print(message, end="")
        for client_id in self.clients:
            client = self.clients[client_id]
            client_socket = client["client_socket"]
            encryption_key = client["public_key"]
            use_encryption = client["encryption"]
            try:
                self.packetIO.write_packet(
                    client_socket, 
                    packet_types.MESSAGE, 
                    message,
                    key=encryption_key,
                    encryption=use_encryption)
            except socket.error as e:
                print(e)

    def handle_date(self, packet, client_id):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        client = self.clients[client_id]
        client_socket = client["client_socket"]
        encryption_key = client["public_key"]
        use_encryption = client["encryption"]
        client_timezone_name = packet[5:packet_len].decode("utf-8")
        client_timezone = ZoneInfo(client_timezone_name)
        now = datetime.now(client_timezone)
        message = format("Server: The date is %s\n" %now.strftime("%A, %B %-d, %Y"))
        self.packetIO.write_packet(
            client_socket,
            packet_types.DATE,
            message,
            key=encryption_key,
            encryption=use_encryption)

    def handle_time(self, packet, client_id):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        client = self.clients[client_id]
        client_socket = client["client_socket"]
        encryption_key = client["public_key"]
        use_encryption = client["encryption"]
        client_timezone_name = packet[5:packet_len].decode("utf-8")
        client_timezone = ZoneInfo(client_timezone_name)
        now = datetime.now(client_timezone)
        message = format("Server: The time is %s\n" %now.strftime("%-I:%M %p %Z"))
        self.packetIO.write_packet(
            client_socket,
            packet_types.TIME,
            message,
            key=encryption_key,
            encryption=use_encryption)

def main():
    config = configparser.ConfigParser()
    config.read("config/server_settings.ini")
    packetIO = PacketIO()
    packetIO.configure_log("server_log.txt", "w")
    packetIO.enable_logging()
    app = Application(config, packetIO)
    app.parse_keys()
    app.load_user_db()
    app.listen()

if __name__ == "__main__":
    main()
