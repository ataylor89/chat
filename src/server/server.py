from server import base_dir
from server.client import Client
from server.client_registry import ClientRegistry
from server.key_manager import KeyManager
from server.user_manager import UserManager
from shared import packet_types
from shared.packet_io import PacketIO
from shared.rsa import parser
from zoneinfo import ZoneInfo
from datetime import datetime
import socket
import threading

class Server:

    def __init__(self, config):
        self.config = config
        self.host = config['socket']['host']
        self.port = int(config['socket']['port'])
        self.packetIO = PacketIO(config)
        self.packetIO.open_log()
        self.users = UserManager()
        self.users.load()
        self.clients = ClientRegistry()
        self.keys = KeyManager(config)
        self.keys.load()

    def listen(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        while True:
            client_socket, client_address = self.server_socket.accept()
            client = self.clients.add_client(client_socket, client_address)
            thread = threading.Thread(target=self.readloop, args=(client,))
            thread.start()

    def readloop(self, client):
        client_id = client.client_id
        client_socket = client.client_socket
        done = False
        while not done:
            try:
                decryption_key = self.keys['private']
                encryption = client.encryption
                packet = self.packetIO.read_packet(client_socket, key=decryption_key, encryption=encryption)
                if packet:
                    self.process(packet, client)
            except socket.error as e:
                done = True
            except Exception as e:
                print(e)
        self.clients.remove_client(client_id)

    def process(self, packet, client):
        packet_type = packet[4]
        if packet_type == packet_types.EXCHANGE_PUBLIC_KEYS:
            self.handle_exchange_public_keys(packet, client)
        elif packet_type == packet_types.CONNECT:
            self.handle_connect(packet, client)
        elif packet_type == packet_types.DISCONNECT:
            self.handle_disconnect(packet, client)
        elif packet_type == packet_types.REGISTER:
            self.handle_registration(packet, client)
        elif packet_type == packet_types.LOGIN:
            self.handle_login(packet, client)
        elif packet_type == packet_types.LOGOUT:
            self.handle_logout(packet, client)
        elif packet_type == packet_types.PROFILE:
            self.handle_profile(packet, client)
        elif packet_type == packet_types.MESSAGE:
            self.handle_message(packet, client)
        elif packet_type == packet_types.WHOAMI:
            self.handle_whoami(packet, client)
        elif packet_type == packet_types.DATE:
            self.handle_date(packet, client)
        elif packet_type == packet_types.TIME:
            self.handle_time(packet, client)

    def userlist(self):
        userlist = []
        for client in self.clients.values():
            if client.encryption:
                display_name = client.get_display_name()
                userlist.append(display_name)
        userlist.sort()
        return userlist

    def handle_exchange_public_keys(self, packet, client):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        client_socket = client.client_socket
        display_name = client.get_display_name()
        client_public_key_encoded = packet[5:packet_len].decode('utf-8')
        client.public_key = parser.decode(client_public_key_encoded)
        packet_body = parser.encode(self.keys['public'])
        encryption_key = client.public_key
        encryption = client.encryption
        self.packetIO.write_packet(client_socket, packet_types.EXCHANGE_PUBLIC_KEYS, packet_body, key=encryption_key, encryption=encryption)
        client.encryption = True
        print('Exchanged public keys with user %s' %display_name)

    def handle_connect(self, packet, client):
        client_name = client.client_name
        connect_packet = format('Server: %s has connected to the server\n' %client_name)
        userlist_packet = ':'.join(self.userlist())
        for cli in self.clients.values():
            cli_socket = cli.client_socket
            encryption_key = cli.public_key
            encryption = cli.encryption
            try:
                self.packetIO.write_packet(cli_socket, packet_types.CONNECT, connect_packet, key=encryption_key, encryption=encryption)
                self.packetIO.write_packet(cli_socket, packet_types.USERLIST, userlist_packet, key=encryption_key, encryption=encryption)
            except socket.error as e:
                print(e)
        print('%s has connected to the server' %client_name)

    def handle_disconnect(self, packet, client):
        display_name = client.get_display_name()
        userlist = self.userlist()
        userlist.remove(display_name)
        disconnect_packet = format('Server: %s has disconnected from the server\n' %display_name)
        userlist_packet = ':'.join(userlist)
        for cli in self.clients.values():
            if cli.client_id == client.client_id:
                continue
            cli_socket = cli.client_socket
            encryption_key = cli.public_key
            encryption = cli.encryption
            try:
                self.packetIO.write_packet(cli_socket, packet_types.DISCONNECT, disconnect_packet, key=encryption_key, encryption=encryption)
                self.packetIO.write_packet(cli_socket, packet_types.USERLIST, userlist_packet, key=encryption_key, encryption=encryption)
            except socket.error as e:
                print(e)
        if client.logged_in:
            self.users.logout(client.username)
        client.client_socket.close()
        print('%s has disconnected from the server' %display_name)

    def handle_registration(self, packet, client):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        client_socket = client.client_socket
        encryption_key = client.public_key
        encryption = client.encryption
        tokens = packet[5:packet_len].decode('utf-8').split(':', 1)
        username = tokens[0]
        password = tokens[1]
        if self.users.register(username, password):
            message = format('Server: The username %s was successfully registered\n' %username)
            self.packetIO.write_packet(client_socket, packet_types.REGISTER, message, key=encryption_key, encryption=encryption)
            print('The username %s was successfully registered' %username)
        else:
            message = format('Server: The username %s is already taken\n' %username)
            self.packetIO.write_packet(client_socket, packet_types.REGISTER, message, key=encryption_key, encryption=encryption)
            print('Unable to register username %s because it is already taken' %username)

    def handle_login(self, packet, client):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        client_name = client.client_name
        tokens = packet[5:packet_len].decode('utf-8').split(':', 1)
        username = tokens[0]
        password = tokens[1] 
        if not client.logged_in and self.users.attempt_login(username, password):
            client.username = username
            client.logged_in = True
            login_packet = format('Server: %s logged in as %s\n' %(client_name, username))
            userlist_packet = ':'.join(self.userlist())
            for cli in self.clients.values():
                cli_socket = cli.client_socket
                encryption_key = cli.public_key
                encryption = cli.encryption
                self.packetIO.write_packet(cli_socket, packet_types.LOGIN, login_packet, key=encryption_key, encryption=encryption)
                self.packetIO.write_packet(cli_socket, packet_types.USERLIST, userlist_packet, key=encryption_key, encryption=encryption)
            self.handle_profile(packet, client)
            print('%s logged in as %s' %(client_name, username))
        else:
            client_socket = client.client_socket
            encryption_key = client.public_key
            encryption = client.encryption
            login_packet = format('Server: Unable to login as %s\n' %username)
            self.packetIO.write_packet(client_socket, packet_types.LOGIN, login_packet, key=encryption_key, encryption=encryption)
            print('%s was unable to login' %client_name)

    def handle_logout(self, packet, client):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        client_name = client.client_name
        username = client.username
        if client.logged_in:
            self.users.logout(username)
            client.username = None
            client.logged_in = False
            logout_packet = format('Server: %s logged out\n' %username)
            userlist_packet = ':'.join(self.userlist())
            for cli in self.clients.values():
                cli_socket = cli.client_socket
                encryption_key = cli.public_key
                encryption = cli.encryption
                try:
                    self.packetIO.write_packet(cli_socket, packet_types.LOGOUT, logout_packet, key=encryption_key, encryption=encryption)
                    self.packetIO.write_packet(cli_socket, packet_types.USERLIST, userlist_packet, key=encryption_key, encryption=encryption)
                except socket.error as e:
                    print(e)
            self.handle_profile(packet, client)
            print('%s logged out' %username)

    def handle_profile(self, packet, client):
        client_name = client.client_name
        client_socket = client.client_socket
        client_address = client.client_address
        client_ip = client_address[0]
        client_port = client_address[1]
        logged_in = client.logged_in
        username = client.username if client.username else 'None'
        template = 'client_name=%s:client_ip=%s:client_port=%d:logged_in=%s:username=%s'
        packet_body = format(template %(client_name, client_ip, client_port, logged_in, username))
        encryption_key = client.public_key
        encryption = client.encryption
        self.packetIO.write_packet(client_socket, packet_types.PROFILE, packet_body, key=encryption_key, encryption=encryption)

    def handle_message(self, packet, client):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        display_name = client.get_display_name()
        packet_body = format('%s: %s' %(display_name, packet[5:packet_len].decode('utf-8')))
        for cli in self.clients.values():
            cli_socket = cli.client_socket
            encryption_key = cli.public_key
            encryption = cli.encryption
            try:
                self.packetIO.write_packet(cli_socket, packet_types.MESSAGE, packet_body, key=encryption_key, encryption=encryption)
            except socket.error as e:
                print(e)
        print(packet_body, end='')

    def handle_whoami(self, packet, client):
        client_name = client.client_name
        client_socket = client.client_socket
        client_address = client.client_address
        client_ip = client_address[0]
        client_port = client_address[1]
        username = client.username if client.username else 'None'
        encryption_key = client.public_key
        encryption = client.encryption
        template = 'Server: whoami results\n'
        template += 'client_name=%s\n'
        template += 'client_ip=%s\n'
        template += 'client_port=%d\n'
        template += 'username=%s\n'
        packet_body = format(template %(client_name, client_ip, client_port, username))
        self.packetIO.write_packet(client_socket, packet_types.WHOAMI, packet_body, key=encryption_key, encryption=encryption)

    def handle_date(self, packet, client):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        client_socket = client.client_socket
        encryption_key = client.public_key
        encryption = client.encryption
        client_timezone_name = packet[5:packet_len].decode('utf-8')
        client_timezone = ZoneInfo(client_timezone_name)
        now = datetime.now(client_timezone)
        message = format('Server: The date is %s\n' %now.strftime('%A, %B %-d, %Y'))
        self.packetIO.write_packet(client_socket, packet_types.DATE, message, key=encryption_key, encryption=encryption)

    def handle_time(self, packet, client):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        client_socket = client.client_socket
        encryption_key = client.public_key
        encryption = client.encryption
        client_timezone_name = packet[5:packet_len].decode('utf-8')
        client_timezone = ZoneInfo(client_timezone_name)
        now = datetime.now(client_timezone)
        message = format('Server: The time is %s\n' %now.strftime('%-I:%M %p %Z'))
        self.packetIO.write_packet(client_socket, packet_types.TIME, message, key=encryption_key, encryption=encryption)
