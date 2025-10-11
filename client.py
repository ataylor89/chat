import tkinter as tk
from tkinter.scrolledtext import ScrolledText
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

class Application(tk.Tk):
    def __init__(self, config, packetIO):
        tk.Tk.__init__(self)
        self.title(config["default"]["title"])
        self.protocol("WM_DELETE_WINDOW", self.close_application)
        self.resizable(False, False)
        self.frame = tk.Frame(self)
        self.frame.pack(fill="both", expand=True)
        self.create_widgets(config)
        self.host = config["default"]["host"]
        self.port = int(config["default"]["port"])
        self.use_encryption = False
        self.keys = {
            "client": {"public": None, "private": None},
            "server": {"public": None, "private": None}
        }
        self.app_is_closing = False
        self.packetIO = packetIO

    def create_widgets(self, config):
        bgcolor = config["default"]["bg"]
        fgcolor = config["default"]["fg"]
        fontname = config["default"]["fontname"]
        fontsize = int(config["default"]["fontsize"])
        self.chat_ta = ScrolledText(self.frame,
            width=80,
            height=30,
            wrap="word", 
            bg=bgcolor,
            fg=fgcolor,
            font=(fontname, fontsize)) 
        self.chat_ta.grid(row=0, column=0)
        self.chat_ta.bind("<Key>", self.handle_key_press)
        self.dm_ta = ScrolledText(self.frame,
            width=80,
            height=6,
            wrap="word",
            bg=bgcolor,
            fg=fgcolor,
            font=(fontname, fontsize))
        self.dm_ta.bind("<Return>", self.handle_return)
        self.dm_ta.grid(row=1, column=0)
        self.userlist_ys = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.userlist_ys.grid(row=0, column=2, rowspan=2, sticky="ns")
        self.userlist_xs = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.userlist_xs.grid(row=2, column=1, sticky="ew")
        self.userlist_lb = tk.Listbox(self.frame, bg=bgcolor, fg=fgcolor)
        self.userlist_lb.config(yscrollcommand=self.userlist_ys.set)
        self.userlist_lb.config(xscrollcommand=self.userlist_xs.set)
        self.userlist_ys.config(command=self.userlist_lb.yview)
        self.userlist_xs.config(command=self.userlist_lb.xview)
        self.userlist_lb.grid(column=1, row=0, rowspan=2, sticky="nsew")

    def handle_key_press(self, event):
        return "break"

    def handle_return(self, event):
        message = self.dm_ta.get("1.0", tk.END)
        if self.is_command(message):
            self.process_command(message)
        else:
            encryption_key = self.keys["server"]["public"]
            self.packetIO.write_packet(self.s, 
                packet_types.MESSAGE, 
                message,
                key=encryption_key,
                encryption=self.use_encryption)
        if not self.app_is_closing:
            self.dm_ta.delete("1.0", tk.END)
            return "break"

    def close_application(self):
        self.disconnect()
        self.readloop_thread.join()
        self.app_is_closing = True
        self.destroy()

    def parse_keys(self):
        self.keys["client"]["public"] = parser.parse_key("rsa/publickey.txt")
        self.keys["client"]["private"] = parser.parse_key("rsa/privatekey.txt")

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))

    def disconnect(self):
        self.s.close()

    def start_readloop(self):
        self.readloop_thread = threading.Thread(target=self.readloop)
        self.readloop_thread.start()

    def register(self, username, password):
        message = username + ":" + password
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s, 
            packet_types.REGISTER, 
            message,
            key=encryption_key,
            encryption=self.use_encryption)

    def join(self):
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s,
            packet_types.JOIN,
            None,
            key=encryption_key,
            encryption=self.use_encryption)

    def leave(self):
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s,
            packet_types.LEAVE,
            None,
            key=encryption_key,
            encryption=self.use_encryption)

    def login(self, username, password):
        message = username + ":" + password
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s, 
            packet_types.LOGIN, 
            message,
            key=encryption_key,
            encryption=self.use_encryption)

    def logout(self):
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s,
            packet_types.LOGOUT,
            None,
            key=encryption_key,
            encryption=self.use_encryption)

    def exchange_public_key(self):
        client_public_key = self.keys["client"]["public"]
        client_public_key = parser.encode(client_public_key)
        encryption_key = self.keys["server"]["public"]
        self.packetIO.write_packet(self.s, 
            packet_types.EXCHANGE_PUBLIC_KEY, 
            client_public_key,
            key=encryption_key,
            encryption=self.use_encryption)

    def get_date(self):
        encryption_key = self.keys["server"]["public"]
        tz_name = tzlocal.get_localzone_name()
        self.packetIO.write_packet(self.s,
            packet_types.DATE,
            tz_name,
            key=encryption_key,
            encryption=self.use_encryption)

    def get_time(self, format=None):
        encryption_key = self.keys["server"]["public"]
        tz_name = tzlocal.get_localzone_name()
        self.packetIO.write_packet(self.s,
            packet_types.TIME,
            tz_name,
            key=encryption_key,
            encryption=self.use_encryption)

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

    def process(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        packet_type = packet[4]
        if packet_type == packet_types.EXCHANGE_PUBLIC_KEY:
            self.handle_exchange_public_key(packet)
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
        elif packet_type == packet_types.DATE:
            self.handle_date(packet)
        elif packet_type == packet_types.TIME:
            self.handle_time(packet)

    def handle_exchange_public_key(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        server_public_key = packet[5:packet_len].decode("utf-8")
        self.keys["server"]["public"] = parser.decode(server_public_key)
        self.use_encryption = True

    def handle_join(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.chat_ta.insert(tk.END, message)

    def handle_leave(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.chat_ta.insert(tk.END, message)

    def handle_register(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.chat_ta.insert(tk.END, message)

    def handle_login(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.chat_ta.insert(tk.END, message)

    def handle_logout(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.chat_ta.insert(tk.END, message)

    def handle_userlist(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        packet_body = packet[5:packet_len].decode("utf-8")
        userlist = packet_body.split(":")
        self.userlist_lb.delete(0, tk.END)
        for username in userlist:
            self.userlist_lb.insert(tk.END, username)

    def handle_message(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.chat_ta.insert(tk.END, message)

    def handle_date(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.chat_ta.insert(tk.END, message)

    def handle_time(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.chat_ta.insert(tk.END, message)

    def is_command(self, message):
        tokens = message.strip().split(" ")
        if tokens[0].startswith("/") and tokens[0] in cmdlist:
            return True

    def process_command(self, message):
        cmdname = message.strip().split()[0]
        if cmdname == "/register":
            tokens = message.strip().split()
            username = tokens[1]
            password = tokens[2]
            self.register(username, password)
        elif cmdname == "/join":
            self.join()
        elif cmdname == "/leave":
            self.leave()
        elif cmdname == "/login":
            tokens = message.strip().split()
            username = tokens[1]
            password = tokens[2]
            self.login(username, password)
        elif cmdname == "/logout":
            self.logout()
        elif cmdname == "/date":
            self.get_date()
        elif cmdname == "/time":
            self.get_time()
        elif cmdname == "/exit":
            self.close_application()

def main():
    config = configparser.ConfigParser()
    config.read("config/client_settings.ini")
    packetIO = PacketIO()
    packetIO.configure_log("client_log.txt", "w")
    packetIO.enable_logging()
    app = Application(config, packetIO)
    app.parse_keys()
    app.connect()
    app.start_readloop()
    app.exchange_public_key()
    while not app.use_encryption:
        time.sleep(1)
    app.mainloop()

if __name__ == "__main__":
    main()
