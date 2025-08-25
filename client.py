# This is also a work in progress and eventually I will create a gui for the client

import pio
import ptypes
import socket
import threading
import time
from datetime import datetime
from rsa import parser

host = "127.0.0.1"
port = 12345

keys = {"client": {}, "server": {}}

def main():
    parse_keys()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    thread = threading.Thread(target=readloop, args=(s,))
    thread.start()
    register(s, "ktm5124", "testpassword")
    login(s, "ktm5124", "testpassword")
    exchange_public_key(s)
    while True:
        message = format("The time is %s" %datetime.now().strftime("%I:%M:%S %p"))
        pio.write_packet(s, ptypes.MESSAGE, message)
        time.sleep(60)

def parse_keys():
    keys["client"]["public"] = parser.parse_key("rsa/publickey.txt")
    keys["client"]["private"] = parser.parse_key("rsa/privatekey.txt")

def register(s, username, password):
    message = username + ":" + password
    pio.write_packet(s, ptypes.REGISTER, message)

def login(s, username, password):
    message = username + ":" + password
    pio.write_packet(s, ptypes.LOGIN, message)

def exchange_public_key(s):
    client_public_key = keys["client"]["public"]
    client_public_key_enc = parser.encode(client_public_key)
    print("The client's public key is %s" %client_public_key_enc)
    pio.write_packet(s, ptypes.EXCHANGE_PUBLIC_KEY, client_public_key_enc)

def readloop(s):
    done = False
    while not done:
        try:
            packet = pio.read_packet(s)
            if packet:
                process(packet)
        except socket.error as e:
            print(e)
            s.close()
            done = True

def process(packet):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    packet_type = packet[4]
    if packet_type == ptypes.EXCHANGE_PUBLIC_KEY:
        handle_exchange_public_key(packet)
    elif packet_type == ptypes.REGISTER:
        handle_register(packet)
    elif packet_type == ptypes.LOGIN:
        handle_login(packet)
    elif packet_type == ptypes.MESSAGE:
        handle_message(packet)

def handle_exchange_public_key(packet):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    server_public_key_enc = packet[5:packet_len].decode("utf-8")
    print("The server's public key is %s" %server_public_key_enc)
    keys["server"]["public"] = parser.decode(server_public_key_enc)

def handle_register(packet):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    message = packet[5:packet_len].decode("utf-8")
    print(message)

def handle_login(packet):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    message = packet[5:packet_len].decode("utf-8")
    print(message)

def handle_message(packet):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    message = packet[5:packet_len].decode("utf-8")
    print(message)

if __name__ == "__main__":
    main()
