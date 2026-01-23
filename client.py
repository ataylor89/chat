#!/usr/bin/env python3

from gui import GUI
from packet_io import PacketIO
import packet_types
from cmdlist import cmdlist
from rsa import parser
import socket
import threading
import time
from datetime import datetime
import tzlocal
import configparser
import sys

class Client:

    def __init__(self, config):
        self.config = config
        self.project_root = sys.path[0]
        self.packetIO = PacketIO(config)
        self.packetIO.open_log()
        self.host = config['default']['host']
        self.port = int(config['default']['port'])
        self.sock = None
        self.connected = False
        self.encryption = False
        self.client_ip = None
        self.client_port = None
        self.client_name = None
        self.logged_in = False
        self.username = None
        self.keys = {
            'client': {'public': None, 'private': None},
            'server': {'public': None, 'private': None}
        }
        self.parse_keys()

    def set_gui(self, gui):
        self.gui = gui

    def parse_keys(self):
        public_key_file = self.config['default']['public_key_file']

        if not public_key_file.startswith('/'):
            public_key_file = self.project_root + '/' + public_key_file

        private_key_file = self.config['default']['private_key_file']

        if not private_key_file.startswith('/'):
            private_key_file = self.project_root + '/' + private_key_file

        self.keys['client']['public'] = parser.parse_key(public_key_file)
        self.keys['client']['private'] = parser.parse_key(private_key_file)

    def readloop(self):
        done = False
        while not done:
            try:
                decryption_key = self.keys['client']['private']
                packet = self.packetIO.read_packet(self.sock, decryption_key)
                if packet:
                    self.process(packet)
            except socket.error as e:
                done = True
            except Exception as e:
                print(e)
        self.sock = None
        self.connected = False
        self.encryption = False
        self.logged_in = False

    def process(self, packet):
        packet_type = packet[4]
        if packet_type == packet_types.EXCHANGE_PUBLIC_KEYS:
            self.handle_exchange_public_keys(packet)
        elif packet_type == packet_types.CONNECT:
            self.handle_connect(packet)
        elif packet_type == packet_types.DISCONNECT:
            self.handle_disconnect(packet)
        elif packet_type == packet_types.REGISTER:
            self.handle_register(packet)
        elif packet_type == packet_types.LOGIN:
            self.handle_login(packet)
        elif packet_type == packet_types.LOGOUT:
            self.handle_logout(packet)
        elif packet_type == packet_types.PROFILE:
            self.handle_profile(packet)
        elif packet_type == packet_types.USERLIST:
            self.handle_userlist(packet)
        elif packet_type == packet_types.MESSAGE:
            self.handle_message(packet)
        elif packet_type == packet_types.WHOAMI:
            self.handle_whoami(packet)
        elif packet_type == packet_types.DATE:
            self.handle_date(packet)
        elif packet_type == packet_types.TIME:
            self.handle_time(packet)

    def exchange_public_keys(self):
        if not self.connected:
            return
        client_public_key = self.keys['client']['public']
        client_public_key_encoded = parser.encode(client_public_key)
        encryption_key = self.keys['server']['public'] if self.encryption else None
        self.packetIO.write_packet(self.sock, packet_types.EXCHANGE_PUBLIC_KEYS, client_public_key_encoded, encryption_key)

    def connect(self, host, port):
        if self.connected:
            return
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            self.connected = True
            self.readloop_thread = threading.Thread(target=self.readloop)
            self.readloop_thread.start()
            self.exchange_public_keys()
            while not self.encryption:
                time.sleep(0.005) # 5 milliseconds
            encryption_key = self.keys['server']['public']
            self.packetIO.write_packet(self.sock, packet_types.CONNECT, None, encryption_key)
        except Exception as e:
            print(e)

    def notify_disconnect(self, callback):
        if not self.connected:
            return
        encryption_key = self.keys['server']['public']
        self.packetIO.write_packet(self.sock, packet_types.DISCONNECT, None, encryption_key, callback)

    def disconnect(self):
        self.gui.add_message('Disconnected from the server\n')
        self.gui.clear_userlist()
        if self.sock:
            self.sock.close()
            self.readloop_thread.join()

    def register(self, username, password):
        if not self.encryption:
            return
        message = username + ':' + password
        encryption_key = self.keys['server']['public']
        self.packetIO.write_packet(self.sock, packet_types.REGISTER, message, encryption_key)

    def login(self, username, password):
        if not self.encryption:
            return
        message = username + ':' + password
        encryption_key = self.keys['server']['public']
        self.packetIO.write_packet(self.sock, packet_types.LOGIN, message, encryption_key)

    def logout(self):
        if not self.logged_in:
            return
        encryption_key = self.keys['server']['public']
        self.packetIO.write_packet(self.sock, packet_types.LOGOUT, None, encryption_key)

    def send_message(self, message):
        if not self.encryption:
            return
        encryption_key = self.keys['server']['public']
        self.packetIO.write_packet(self.sock, packet_types.MESSAGE, message, encryption_key)

    def whoami(self):
        if not self.encryption:
            return
        encryption_key = self.keys['server']['public']
        self.packetIO.write_packet(self.sock, packet_types.WHOAMI, None, encryption_key)

    def get_date(self):
        if not self.encryption:
            return
        encryption_key = self.keys['server']['public']
        tz_name = tzlocal.get_localzone_name()
        self.packetIO.write_packet(self.sock, packet_types.DATE, tz_name, encryption_key)

    def get_time(self):
        if not self.encryption:
            return
        encryption_key = self.keys['server']['public']
        tz_name = tzlocal.get_localzone_name()
        self.packetIO.write_packet(self.sock, packet_types.TIME, tz_name, encryption_key)

    def exit(self):
        if self.sock:
            self.sock.close()
            self.readloop_thread.join()
        self.gui.app_is_closing = True
        self.gui.destroy()

    def handle_exchange_public_keys(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        server_public_key_encoded = packet[5:packet_len].decode('utf-8')
        self.keys['server']['public'] = parser.decode(server_public_key_encoded)
        self.encryption = True

    def handle_connect(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        message = packet[5:packet_len].decode('utf-8')
        self.gui.add_message(message)

    def handle_disconnect(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        message = packet[5:packet_len].decode('utf-8')
        self.gui.add_message(message)

    def handle_register(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        message = packet[5:packet_len].decode('utf-8')
        self.gui.add_message(message)

    def handle_login(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        message = packet[5:packet_len].decode('utf-8')
        self.gui.add_message(message)

    def handle_logout(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        message = packet[5:packet_len].decode('utf-8')
        self.gui.add_message(message)

    def handle_profile(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        body = packet[5:packet_len].decode('utf-8')
        tokens = body.split(':')
        self.client_name = tokens[0][12:]
        self.client_ip = tokens[1][10:]
        self.client_port = int(tokens[2][12:])
        self.logged_in = tokens[3][10:] == 'True'
        self.username = tokens[4][9:] if tokens[4][9:] != 'None' else None

    def handle_userlist(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        packet_body = packet[5:packet_len].decode('utf-8')
        userlist = packet_body.split(':')
        self.gui.clear_userlist()
        for username in userlist:
            self.gui.add_user(username)

    def handle_message(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        message = packet[5:packet_len].decode('utf-8')
        self.gui.add_message(message)

    def handle_whoami(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        message = packet[5:packet_len].decode('utf-8')
        self.gui.add_message(message)

    def handle_date(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        message = packet[5:packet_len].decode('utf-8')
        self.gui.add_message(message)

    def handle_time(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder='big', signed=False)
        message = packet[5:packet_len].decode('utf-8')
        self.gui.add_message(message)

    def is_command(self, message):
        tokens = message.strip().split(' ')
        if tokens[0].startswith('/') and tokens[0] in cmdlist:
            return True

    def process_command(self, message):
        cmdname = message.strip().split()[0]
        if cmdname == '/connect':
            tokens = message.strip().split()
            if len(tokens) == 3:
                host = tokens[1]
                port = int(tokens[2])
                self.connect(host, port)
            else:
                self.connect(self.host, self.port)
        elif cmdname == '/disconnect':
            self.notify_disconnect(self.disconnect)
        elif cmdname == '/register':
            tokens = message.strip().split()
            username = tokens[1]
            password = tokens[2]
            self.register(username, password)
        elif cmdname == '/login':
            tokens = message.strip().split()
            username = tokens[1]
            password = tokens[2]
            self.login(username, password)
        elif cmdname == '/logout':
            self.logout()
        elif cmdname == '/whoami':
            self.whoami()
        elif cmdname == '/date':
            self.get_date()
        elif cmdname == '/time':
            self.get_time()
        elif cmdname == '/exit':
            if self.connected:
                self.notify_disconnect(self.exit)
            else:
                self.exit()

def main():
    config = configparser.ConfigParser()
    project_root = sys.path[0]
    config_file = f'{project_root}/config/client_settings.ini'
    config.read(config_file)
    cli = Client(config)
    gui = GUI(config)
    gui.set_client(cli)
    cli.set_gui(gui)
    gui.mainloop()

if __name__ == '__main__':
    main()
