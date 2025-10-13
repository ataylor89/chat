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

class Server:
    def __init__(self, config, packetIO):
        self.host = config["default"]["host"]
        self.port = int(config["default"]["port"])
        self.clients = {}
        self.users = {}
        self.logged_in_users = []
        self.rsa_keys = {}
        self.packetIO = packetIO

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
            "active": False,
            "logged_in": False,
            "username": None
        }

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
                done = True
            except Exception as e:
                print(e)
        del self.clients[client_id]

    def process(self, packet, client_id):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        packet_type = packet[4]
        if packet_type == packet_types.CONNECT:
            self.handle_connect(packet, client_id)
        elif packet_type == packet_types.DISCONNECT:
            self.handle_disconnect(packet, client_id)
        elif packet_type == packet_types.ENCRYPTION_ON:
            self.handle_encryption_on(packet, client_id)
        elif packet_type == packet_types.ENCRYPTION_OFF:
            self.handle_encryption_off(packet, client_id)
        elif packet_type == packet_types.JOIN:
            self.handle_join(packet, client_id)
        elif packet_type == packet_types.LEAVE:
            self.handle_leave(packet, client_id)
        elif packet_type == packet_types.REGISTER:
            self.handle_registration(packet, client_id)
        elif packet_type == packet_types.LOGIN:
            self.handle_login(packet, client_id)
        elif packet_type == packet_types.LOGOUT:
            self.handle_logout(packet, client_id)
        elif packet_type == packet_types.MESSAGE:
            self.handle_message(packet, client_id)
        elif packet_type == packet_types.WHOAMI:
            self.handle_whoami(packet, client_id)
        elif packet_type == packet_types.DATE:
            self.handle_date(packet, client_id)
        elif packet_type == packet_types.TIME:
            self.handle_time(packet, client_id)

    def userlist(self):
        ul = []
        for client_id in self.clients:
            client = self.clients[client_id]
            if client["active"]:
                username = client["username"] if client["username"] else client["client_name"]
                ul.append(username)
        ul.sort()
        return ul

    def handle_connect(self, packet, client_id):
        client = self.clients[client_id]
        client_name = client["client_name"]
        client_socket = client["client_socket"]
        encryption_key = client["public_key"]
        use_encryption = client["encryption"]
        packet_body = format("Server: %s has connected to the server\n" %client_name)
        self.packetIO.write_packet(
            client_socket,
            packet_types.CONNECT,
            packet_body,
            key=encryption_key,
            encryption=use_encryption)
        print("%s has connected to the server" %client_name)

    def handle_disconnect(self, packet, client_id):
        client = self.clients[client_id]
        client_name = client["client_name"]
        client_socket = client["client_socket"]
        encryption_key = client["public_key"]
        use_encryption = client["encryption"]
        username = client["username"] if client["username"] else client["client_name"]
        packet_body = format("Server: %s has disconnected from the server\n" %username)
        self.packetIO.write_packet(
            client_socket,
            packet_types.DISCONNECT,
            packet_body,
            key=encryption_key,
            encryption=use_encryption)
        client_socket.close()
        print("%s has disconnected from the server" %username)

    def handle_encryption_on(self, packet, client_id):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        client = self.clients[client_id]
        client_name = client["client_name"]
        client_socket = client["client_socket"]
        username = client["username"] if client["username"] else client_name
        client_public_key_enc = packet[5:packet_len].decode("utf-8")
        client["public_key"] = parser.decode(client_public_key_enc)
        server_public_key = parser.parse_key("rsa/publickey.txt")
        server_public_key_enc = parser.encode(server_public_key)
        encryption_key = client["public_key"]
        use_encryption = client["encryption"]
        packet_body = format("Server: Encryption turned on for %s\n" %username)
        packet_body += ":"
        packet_body += server_public_key_enc
        self.packetIO.write_packet(
            client_socket, 
            packet_types.ENCRYPTION_ON, 
            packet_body, 
            key=encryption_key, 
            encryption=use_encryption)
        client["encryption"] = True
        print("Encryption turned on for %s" %username)

    def handle_encryption_off(self, packet, client_id):
        client = self.clients[client_id]
        client_socket = client["client_socket"]
        encryption_key = client["public_key"]
        use_encryption = client["encryption"]
        username = client["username"] if client["username"] else client["client_name"]
        packet_body = format("Server: Encryption turned off for %s\n" %username)
        self.packetIO.write_packet(
            client_socket,
            packet_types.ENCRYPTION_OFF,
            packet_body,
            key=encryption_key,
            encryption=use_encryption)
        client["encryption"] = False
        print("Encryption turned off for %s" %username)

    def handle_join(self, packet, client_id):
        client = self.clients[client_id]
        client["active"] = True
        client_name = client["client_name"]
        join_packet = format("Server: %s joined the chat room\n" %client_name)
        userlist_packet = ":".join(self.userlist())
        for cli_id in self.clients:
            cli = self.clients[cli_id] 
            cli_socket = cli["client_socket"]
            encryption_key = cli["public_key"]
            use_encryption = cli["encryption"]
            try:
                self.packetIO.write_packet(
                    cli_socket,
                    packet_types.JOIN,
                    join_packet,
                    key=encryption_key,
                    encryption=use_encryption)
                self.packetIO.write_packet(
                    cli_socket,
                    packet_types.USERLIST,
                    userlist_packet,
                    key=encryption_key,
                    encryption=use_encryption)
            except socket.error as e:
                print(e)
        print("%s joined the chat room" %client_name)

    def handle_leave(self, packet, client_id):
        client = self.clients[client_id]
        username = client["username"] if client["username"] else client["client_name"]
        if client["logged_in"]:
            self.logged_in_users.remove(username)
        client["active"] = False
        client["logged_in"] = False
        leave_packet = format("Server: %s left the chat room\n" %username)
        userlist_packet = ":".join(self.userlist())
        for cli_id in self.clients:
            cli = self.clients[cli_id]
            cli_socket = cli["client_socket"]
            encryption_key = cli["public_key"]
            use_encryption = cli["encryption"]
            try:
                self.packetIO.write_packet(
                    cli_socket,
                    packet_types.LEAVE,
                    leave_packet,
                    key=encryption_key,
                    encryption=use_encryption)
                self.packetIO.write_packet(
                    cli_socket,
                    packet_types.USERLIST,
                    userlist_packet,
                    key=encryption_key,
                    encryption=use_encryption)
            except socket.error as e:
                print(e)
        print("%s left the chat room" %username)

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
        tokens = packet[5:packet_len].decode("utf-8").split(":", 1)
        username = tokens[0]
        password = tokens[1] 
        if username in self.users and password == self.users[username]["password"] and username not in self.logged_in_users:
            client["username"] = username
            client["logged_in"] = True
            login_packet = format("Server: %s logged in as %s\n" %(client_name, username))
            userlist_packet = ":".join(self.userlist())
            for cli_id in self.clients:
                cli = self.clients[cli_id]
                cli_socket = cli["client_socket"]
                encryption_key = cli["public_key"]
                use_encryption = cli["encryption"]
                self.packetIO.write_packet(
                    cli_socket, 
                    packet_types.LOGIN, 
                    login_packet,
                    key=encryption_key,
                    encryption=use_encryption)
                self.packetIO.write_packet(
                    cli_socket,
                    packet_types.USERLIST,
                    userlist_packet,
                    key=encryption_key,
                    encryption=use_encryption)
            self.logged_in_users.append(username)
            print("%s logged in as %s" %(client_name, username))
        else:
            login_packet = format("Server: Unable to login as %s\n" %username)
            self.packetIO.write_packet(
                client_socket, 
                packet_types.LOGIN, 
                login_packet,
                key=encryption_key,
                encryption=use_encryption)
            print("%s was unable to login" %client_name)

    def handle_logout(self, packet, client_id):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        client = self.clients[client_id]
        client_name = client["client_name"]
        username = client["username"]
        if client["logged_in"]:
            client["username"] = None
            client["logged_in"] = False
            self.logged_in_users.remove(username)
            logout_packet = format("Server: %s logged out\n" %username)
            userlist_packet = ":".join(self.userlist())
            for cli_id in self.clients:
                cli = self.clients[cli_id]
                cli_socket = cli["client_socket"]
                encryption_key = cli["public_key"]
                use_encryption = cli["encryption"]
                try:
                    self.packetIO.write_packet(
                        cli_socket,
                        packet_types.LOGOUT,
                        logout_packet,
                        key=encryption_key,
                        encryption=use_encryption)
                    self.packetIO.write_packet(
                        cli_socket,
                        packet_types.USERLIST,
                        userlist_packet,
                        key=encryption_key,
                        encryption=use_encryption)
                except socket.error as e:
                    print(e)
            print("%s logged out\n" %username)

    def handle_message(self, packet, client_id):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        client = self.clients[client_id]
        username = client["username"] if client["logged_in"] else client["client_name"]
        packet_body = format("%s: %s" %(username, packet[5:packet_len].decode("utf-8")))
        for cli_id in self.clients:
            cli = self.clients[cli_id]
            cli_socket = cli["client_socket"]
            encryption_key = cli["public_key"]
            use_encryption = cli["encryption"]
            try:
                self.packetIO.write_packet(
                    cli_socket, 
                    packet_types.MESSAGE, 
                    packet_body,
                    key=encryption_key,
                    encryption=use_encryption)
            except socket.error as e:
                print(e)
        print(packet_body, end="")

    def handle_whoami(self, packet, client_id):
        client = self.clients[client_id]
        client_name = client["client_name"]
        client_socket = client["client_socket"]
        client_address = client["client_address"]
        client_ip = client_address[0]
        client_port = client_address[1]
        username = client["username"] if client["username"] else "None"
        encryption_key = client["public_key"]
        use_encryption = client["encryption"]
        format_str = "Server: whoami results\n"
        format_str += "client_name=%s\n"
        format_str += "client_ip=%s\n"
        format_str += "client_port=%d\n"
        format_str += "username=%s\n"
        packet_body = format(format_str %(client_name, client_ip, client_port, username))
        self.packetIO.write_packet(
            client_socket,
            packet_types.WHOAMI,
            packet_body,
            key=encryption_key,
            encryption=use_encryption)

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
    packetIO.open_log("server_log.txt", "w")
    server = Server(config, packetIO)
    server.parse_keys()
    server.load_user_db()
    server.listen()

if __name__ == "__main__":
    main()
