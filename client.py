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

class Client:
    def __init__(self, config, packetIO):
        self.config = config
        self.packetIO = packetIO
        self.host = config["default"]["host"]
        self.port = int(config["default"]["port"])
        self.s = None
        self.connected = False
        self.use_encryption = False
        self.keys = {
            "client": {"public": None, "private": None},
            "server": {"public": None, "private": None}
        }

    def set_gui(self, gui):
        self.gui = gui

    def parse_keys(self):
        self.keys["client"]["public"] = parser.parse_key("rsa/publickey.txt")
        self.keys["client"]["private"] = parser.parse_key("rsa/privatekey.txt")

    def reset(self):
        self.s = None
        self.connected = False
        self.use_encryption = False

    def readloop(self):
        done = False
        while not done:
            try:
                decryption_key = self.keys["client"]["private"]
                packet = self.packetIO.read_packet(self.s, key=decryption_key, encryption=self.use_encryption)
                if packet:
                    self.process(packet)
            except socket.error as e:
                print(e)
                done = True
            except Exception as e:
                print(e)
        self.reset()

    def process(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        packet_type = packet[4]
        if packet_type == packet_types.CONNECT:
            self.handle_connect(packet)
        elif packet_type == packet_types.DISCONNECT:
            self.handle_disconnect(packet)
        elif packet_type == packet_types.ENCRYPTION_ON:
            self.handle_encryption_on(packet)
        elif packet_type == packet_types.ENCRYPTION_OFF:
            self.handle_encryption_off(packet)
        elif packet_type == packet_types.JOIN:
            self.handle_join(packet)
        elif packet_type == packet_types.LEAVE:
            self.handle_leave(packet)
        elif packet_type == packet_types.REGISTER:
            self.handle_register(packet)
        elif packet_type == packet_types.LOGIN:
            self.handle_login(packet)
        elif packet_type == packet_types.LOGOUT:
            self.handle_logout(packet)
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

    def connect(self, host, port):
        if self.connected:
            return
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((host, port))
            self.connected = True
            self.readloop_thread = threading.Thread(target=self.readloop)
            self.readloop_thread.start()
            self.packetIO.write_packet(self.s,
                packet_types.CONNECT,
                None,
                key=None,
                encryption=False)
        except Exception as e:
            print(e)
            if self.s:
                self.s.close()
            if self.readloop_thread:
                self.readloop_thread.join()
            else:
                self.reset()

    def disconnect(self):
        if not self.connected:
            return
        self.packetIO.write_packet(self.s,
            packet_types.DISCONNECT,
            None,
            key=None,
            encryption=False)

    def encryption_on(self):
        if not self.connected:
            return
        self.parse_keys()
        client_public_key = self.keys["client"]["public"]
        client_public_key = parser.encode(client_public_key)
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s,
            packet_types.ENCRYPTION_ON,
            client_public_key,
            key=encryption_key,
            encryption=self.use_encryption)

    def encryption_off(self):
        if not self.connected:
            return
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s,
            packet_types.ENCRYPTION_OFF,
            None,
            key=encryption_key,
            encryption=self.use_encryption)

    def join(self):
        if not self.connected:
            return
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s,
            packet_types.JOIN,
            None,
            key=encryption_key,
            encryption=self.use_encryption)

    def leave(self):
        if not self.connected:
            return
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s,
            packet_types.LEAVE,
            None,
            key=encryption_key,
            encryption=self.use_encryption)

    def register(self, username, password):
        if not self.connected:
            return
        message = username + ":" + password
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s, 
            packet_types.REGISTER, 
            message,
            key=encryption_key,
            encryption=self.use_encryption)

    def login(self, username, password):
        if not self.connected:
            return
        message = username + ":" + password
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s, 
            packet_types.LOGIN, 
            message,
            key=encryption_key,
            encryption=self.use_encryption)

    def logout(self):
        if not self.connected:
            return
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s,
            packet_types.LOGOUT,
            None,
            key=encryption_key,
            encryption=self.use_encryption)

    def send_message(self, message):
        if not self.connected:
            return
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s, 
            packet_types.MESSAGE, 
            message,
            key=encryption_key,
            encryption=self.use_encryption)

    def whoami(self):
        if not self.connected:
            return
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s,
            packet_types.WHOAMI,
            None,
            key=encryption_key,
            encryption=self.use_encryption)

    def get_date(self):
        if not self.connected:
            return
        encryption_key = self.keys["server"]["public"]
        tz_name = tzlocal.get_localzone_name()
        self.packetIO.write_packet(self.s,
            packet_types.DATE,
            tz_name,
            key=encryption_key,
            encryption=self.use_encryption)

    def get_time(self):
        if not self.connected:
            return
        encryption_key = self.keys["server"]["public"]
        tz_name = tzlocal.get_localzone_name()
        self.packetIO.write_packet(self.s,
            packet_types.TIME,
            tz_name,
            key=encryption_key,
            encryption=self.use_encryption)

    def exit(self):
        if self.s:
            self.packetIO.write_packet(self.s,
                packet_types.DISCONNECT,
                None,
                key=None,
                encryption=False)
            self.s.close()
            self.readloop_thread.join()
        self.gui.app_is_closing = True
        self.gui.destroy()

    def handle_connect(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.gui.add_message(message)

    def handle_disconnect(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.gui.add_message(message)
        if self.s:
            self.s.close()

    def handle_encryption_on(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        packet_body = packet[5:packet_len].decode("utf-8")
        index = packet_body.find(":")
        index = packet_body.find(":", index+1)
        message = packet_body[0:index]
        server_public_key = packet_body[index+1:]
        self.gui.add_message(message)
        self.keys["server"]["public"] = parser.decode(server_public_key)
        self.use_encryption = True

    def handle_encryption_off(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.gui.add_message(message)
        self.use_encryption = False

    def handle_join(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.gui.add_message(message)

    def handle_leave(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.gui.add_message(message)

    def handle_register(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.gui.add_message(message)

    def handle_login(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.gui.add_message(message)

    def handle_logout(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.gui.add_message(message)

    def handle_userlist(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        packet_body = packet[5:packet_len].decode("utf-8")
        userlist = packet_body.split(":")
        self.gui.clear_userlist()
        for username in userlist:
            self.gui.add_user(username)

    def handle_message(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.gui.add_message(message)

    def handle_whoami(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.gui.add_message(message)

    def handle_date(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.gui.add_message(message)

    def handle_time(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.gui.add_message(message)

    def is_command(self, message):
        tokens = message.strip().split(" ")
        if tokens[0].startswith("/") and tokens[0] in cmdlist:
            return True

    def process_command(self, message):
        cmdname = message.strip().split()[0]
        if cmdname == "/connect":
            tokens = message.strip().split()
            if len(tokens) == 3:
                host = tokens[1]
                port = int(tokens[2])
                self.connect(host, port)
            else:
                self.connect(self.host, self.port)
        elif cmdname == "/disconnect":
            self.disconnect()
        elif cmdname == "/encryption":
            tokens = message.strip().split()
            if len(tokens) == 2:
                if tokens[1] == "on":
                    self.encryption_on()
                elif tokens[1] == "off":
                    self.encryption_off()
        elif cmdname == "/join":
            self.join()
        elif cmdname == "/leave":
            self.leave()
        elif cmdname == "/register":
            tokens = message.strip().split()
            username = tokens[1]
            password = tokens[2]
            self.register(username, password)
        elif cmdname == "/login":
            tokens = message.strip().split()
            username = tokens[1]
            password = tokens[2]
            self.login(username, password)
        elif cmdname == "/logout":
            self.logout()
        elif cmdname == "/whoami":
            self.whoami()
        elif cmdname == "/date":
            self.get_date()
        elif cmdname == "/time":
            self.get_time()
        elif cmdname == "/exit":
            self.exit()

def main():
    config = configparser.ConfigParser()
    config.read("config/client_settings.ini")
    packetIO = PacketIO()
    packetIO.open_log("client_log.txt", "w")
    cli = Client(config, packetIO)
    gui = GUI(config, cli)
    cli.set_gui(gui)
    gui.mainloop()

if __name__ == "__main__":
    main()
