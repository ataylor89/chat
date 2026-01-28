from client.cmdlist import cmdlist
from client.key_manager import KeyManager
from shared import packet_types
from shared.packet_io import PacketIO
from shared.rsa import parser
from datetime import datetime
import socket
import threading
import time
import tzlocal

class Client:

    def __init__(self, config):
        self.config = config
        self.packetIO = PacketIO(config)
        self.host = config['socket']['host']
        self.port = int(config['socket']['port'])
        self.sock = None
        self.connected = False
        self.encryption = False
        self.client_ip = None
        self.client_port = None
        self.client_name = None
        self.logged_in = False
        self.username = None
        self.keys = KeyManager(config)
        self.keys.load()

    def set_gui(self, gui):
        self.gui = gui

    def readloop(self):
        done = False
        while not done:
            try:
                decryption_key = self.keys['client']['private']
                packet = self.packetIO.read_packet(self.sock, key=decryption_key, encryption=self.encryption)
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
        packet_body = parser.encode(client_public_key)
        encryption_key = self.keys['server']['public']
        self.packetIO.write_packet(self.sock, packet_types.EXCHANGE_PUBLIC_KEYS, packet_body, key=encryption_key, encryption=self.encryption)

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
            self.packetIO.write_packet(self.sock, packet_types.CONNECT, None, key=encryption_key, encryption=self.encryption)
        except Exception as e:
            print(e)

    def notify_disconnect(self, callback):
        if not self.connected:
            return
        encryption_key = self.keys['server']['public']
        self.packetIO.write_packet(self.sock, packet_types.DISCONNECT, None, key=encryption_key, encryption=self.encryption, callback=callback)

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
        self.packetIO.write_packet(self.sock, packet_types.REGISTER, message, key=encryption_key, encryption=self.encryption)

    def login(self, username, password):
        if not self.encryption:
            return
        message = username + ':' + password
        encryption_key = self.keys['server']['public']
        self.packetIO.write_packet(self.sock, packet_types.LOGIN, message, key=encryption_key, encryption=self.encryption)

    def logout(self):
        if not self.logged_in:
            return
        encryption_key = self.keys['server']['public']
        self.packetIO.write_packet(self.sock, packet_types.LOGOUT, None, key=encryption_key, encryption=self.encryption)

    def send_message(self, message):
        if not self.encryption:
            return
        encryption_key = self.keys['server']['public']
        self.packetIO.write_packet(self.sock, packet_types.MESSAGE, message, key=encryption_key, encryption=self.encryption)

    def whoami(self):
        if not self.encryption:
            return
        encryption_key = self.keys['server']['public']
        self.packetIO.write_packet(self.sock, packet_types.WHOAMI, None, key=encryption_key, encryption=self.encryption)

    def get_date(self):
        if not self.encryption:
            return
        encryption_key = self.keys['server']['public']
        tz_name = tzlocal.get_localzone_name()
        self.packetIO.write_packet(self.sock, packet_types.DATE, tz_name, key=encryption_key, encryption=self.encryption)

    def get_time(self):
        if not self.encryption:
            return
        encryption_key = self.keys['server']['public']
        tz_name = tzlocal.get_localzone_name()
        self.packetIO.write_packet(self.sock, packet_types.TIME, tz_name, key=encryption_key, encryption=self.encryption)

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
