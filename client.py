# This is also a work in progress and eventually I will create a gui for the client

import packet_io
import packet_types
import socket
import threading
import time
from datetime import datetime
from rsa import parser

settings = {
    "host": "127.0.0.1",
    "port": 12345,
    "encryption": False
}

keys = {
    "client": {
        "public": None,
        "private": None
    }, 
    "server": {
        "public": None,
        "private": None
    }
}

def main():
    parse_keys()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((settings["host"], settings["port"]))
    thread = threading.Thread(target=readloop, args=(s,))
    thread.start()
    exchange_public_key(s)
    while not settings["encryption"]:
        time.sleep(1)
    register(s, "ktm5124", "testpassword")
    login(s, "ktm5124", "testpassword")
    while True:
        message = format("The time is %s" %datetime.now().strftime("%I:%M:%S %p"))
        packet_io.write_packet(
            s, 
            packet_types.MESSAGE, 
            message,
            key=keys["server"]["public"],
            encryption=settings["encryption"])
        time.sleep(60)

def parse_keys():
    keys["client"]["public"] = parser.parse_key("rsa/publickey.txt")
    keys["client"]["private"] = parser.parse_key("rsa/privatekey.txt")

def register(s, username, password):
    message = username + ":" + password
    packet_io.write_packet(
        s, 
        packet_types.REGISTER, 
        message,
        key=keys["server"]["public"],
        encryption=settings["encryption"])

def login(s, username, password):
    message = username + ":" + password
    packet_io.write_packet(
        s, 
        packet_types.LOGIN, 
        message,
        key=keys["server"]["public"],
        encryption=settings["encryption"])

def exchange_public_key(s):
    client_public_key = keys["client"]["public"]
    client_public_key = parser.encode(client_public_key)
    print("The client's public key is %s" %client_public_key)
    packet_io.write_packet(
        s, 
        packet_types.EXCHANGE_PUBLIC_KEY, 
        client_public_key,
        key=keys["server"]["public"],
        encryption=settings["encryption"])

def readloop(s):
    done = False
    while not done:
        try:
            packet = packet_io.read_packet(s, key=keys["client"]["private"], encryption=settings["encryption"])
            if packet:
                process(packet)
        except socket.error as e:
            print(e)
            s.close()
            done = True

def process(packet):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    packet_type = packet[4]
    if packet_type == packet_types.EXCHANGE_PUBLIC_KEY:
        handle_exchange_public_key(packet)
    elif packet_type == packet_types.REGISTER:
        handle_register(packet)
    elif packet_type == packet_types.LOGIN:
        handle_login(packet)
    elif packet_type == packet_types.MESSAGE:
        handle_message(packet)

def handle_exchange_public_key(packet):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    server_public_key = packet[5:packet_len].decode("utf-8")
    print("The server's public key is %s" %server_public_key)
    keys["server"]["public"] = parser.decode(server_public_key)
    settings["encryption"] = True

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
