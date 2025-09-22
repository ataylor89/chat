import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import packet_io
import packet_types
import socket
import threading
import time
from datetime import datetime
from rsa import parser
import configparser

class Application(tk.Tk):
    def __init__(self, config):
        tk.Tk.__init__(self)
        self.title(config["default"]["title"])
        self.protocol("WM_DELETE_WINDOW", self.handle_close)
        self.frame = tk.Frame(self)
        self.frame.pack(fill="both", expand=True)
        self.create_widgets(config)
        self.host = config["default"]["host"]
        self.port = int(config["default"]["port"])
        self.use_encryption = False
        self.keys = {
            "client": {
                "public": None,
                "private": None
            },
            "server": {
                "public": None,
                "private": None
            }
        }

    def create_widgets(self, config):
        self.chat_ta = ScrolledText(self.frame,
            width=80,
            height=30,
            wrap="word", 
            bg=config["default"]["bg"],
            fg=config["default"]["fg"],
            font=(config["default"]["fontname"], int(config["default"]["fontsize"])))
        self.chat_ta.grid(column=0, row=0)
        self.chat_ta.bind("<Key>", self.handle_key_press)
        self.dm_ta = ScrolledText(self.frame,
            width=80,
            height=6,
            wrap="word",
            bg=config["default"]["bg"],
            fg=config["default"]["fg"],
            font=(config["default"]["fontname"], int(config["default"]["fontsize"])))
        self.dm_ta.bind("<Return>", self.handle_return)
        self.dm_ta.grid(column=0, row=1)

    def handle_key_press(self, event):
        return "break"

    def handle_return(self, event):
        message = self.dm_ta.get("1.0", tk.END)
        encryption_key = self.keys["server"]["public"]
        packet_io.write_packet(self.s, 
            packet_types.MESSAGE, 
            message,
            key=encryption_key,
            encryption=self.use_encryption)
        self.dm_ta.delete("1.0", tk.END)
        return "break"

    def handle_close(self):
        self.quit()
        self.destroy()

    def parse_keys(self):
        self.keys["client"]["public"] = parser.parse_key("rsa/publickey.txt")
        self.keys["client"]["private"] = parser.parse_key("rsa/privatekey.txt")

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))

    def start_readloop(self):
        self.readloop_thread = threading.Thread(target=self.readloop)
        self.readloop_thread.start()

    def register(self, username, password):
        message = username + ":" + password
        encryption_key = self.keys["server"]["public"]
        packet_io.write_packet(self.s, 
            packet_types.REGISTER, 
            message,
            key=encryption_key,
            encryption=self.use_encryption)

    def login(self, username, password):
        message = username + ":" + password
        encryption_key = self.keys["server"]["public"]
        packet_io.write_packet(self.s, 
            packet_types.LOGIN, 
            message,
            key=encryption_key,
            encryption=self.use_encryption)

    def exchange_public_key(self):
        client_public_key = self.keys["client"]["public"]
        client_public_key = parser.encode(client_public_key)
        encryption_key = self.keys["server"]["public"]
        packet_io.write_packet(self.s, 
            packet_types.EXCHANGE_PUBLIC_KEY, 
            client_public_key,
            key=encryption_key,
            encryption=self.use_encryption)

    def readloop(self):
        done = False
        while not done:
            try:
                decryption_key = self.keys["client"]["private"]
                packet = packet_io.read_packet(self.s, key=decryption_key, encryption=self.use_encryption)
                if packet:
                    self.process(packet)
            except socket.error as e:
                print(e)
                self.s.close()
                done = True

    def process(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        packet_type = packet[4]
        if packet_type == packet_types.EXCHANGE_PUBLIC_KEY:
            self.handle_exchange_public_key(packet)
        elif packet_type == packet_types.REGISTER:
            self.handle_register(packet)
        elif packet_type == packet_types.LOGIN:
            self.handle_login(packet)
        elif packet_type == packet_types.MESSAGE:
            self.handle_message(packet)

    def handle_exchange_public_key(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        server_public_key = packet[5:packet_len].decode("utf-8")
        self.keys["server"]["public"] = parser.decode(server_public_key)
        self.use_encryption = True

    def handle_register(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.chat_ta.insert(tk.END, message)

    def handle_login(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.chat_ta.insert(tk.END, message)

    def handle_message(self, packet):
        packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
        message = packet[5:packet_len].decode("utf-8")
        self.chat_ta.insert(tk.END, message)

def main():
    config = configparser.ConfigParser()
    config.read("settings.ini")
    app = Application(config)
    app.parse_keys()
    app.connect()
    app.start_readloop()
    app.exchange_public_key()
    while not app.use_encryption:
        time.sleep(1)
    app.register("ktm5124", "testpassword")
    app.login("ktm5124", "testpassword")
    app.mainloop()

if __name__ == "__main__":
    main()
