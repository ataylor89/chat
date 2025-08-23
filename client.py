# This is also a work in progress and eventually I will create a gui for the client

import packet_types
import socket
import threading
import time
from datetime import datetime

host = "127.0.0.1"
port = 12345

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    thread = threading.Thread(target=readloop, args=(s,))
    thread.start()

    register(s, "ktm5124", "testpassword")
    login(s, "ktm5124", "testpassword")

    while True:
        message = format("The time is %s" %datetime.now().strftime("%I:%M:%S %p"))
        packet_len = len(message) + 5
        packet = packet_len.to_bytes(4, byteorder="big")
        packet_type = packet_types.MESSAGE
        packet += packet_type.to_bytes(1)
        packet += message.encode("utf-8")
        s.sendall(packet)
        time.sleep(60)

def login(s, username, password):
    login = username + ":" + password
    packet_len = len(login) + 5
    packet = packet_len.to_bytes(4, byteorder="big")
    packet_type = packet_types.LOGIN
    packet += packet_type.to_bytes(1)
    packet += login.encode("utf-8")
    s.sendall(packet)

def register(s, username, password):
    reg = username + ":" + password
    packet_len = len(reg) + 5
    packet = packet_len.to_bytes(4, byteorder="big")
    packet_type = packet_types.REGISTER
    packet += packet_type.to_bytes(1)
    packet += reg.encode("utf-8")
    s.sendall(packet)

def readloop(s):
    done = False
    while not done:
        try:
            data = s.recv(1024)
            if len(data) > 0:
                print(data.decode("utf-8"), end="")
        except socket.error as e:
            print(e)
            s.close()
            done = True

if __name__ == "__main__":
    main()
