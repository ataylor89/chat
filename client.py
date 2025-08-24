# This is also a work in progress and eventually I will create a gui for the client

import pio
import ptypes
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
        pio.write_packet(s, ptypes.MESSAGE, message)
        time.sleep(60)

def login(s, username, password):
    message = username + ":" + password
    pio.write_packet(s, ptypes.LOGIN, message)

def register(s, username, password):
    message = username + ":" + password
    pio.write_packet(s, ptypes.REGISTER, message)

def readloop(s):
    done = False
    while not done:
        try:
            packet = pio.read_packet(s)
            packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
            message = packet[5:packet_len].decode("utf-8")
            print(message, end="")
        except socket.error as e:
            print(e)
            s.close()
            done = True

if __name__ == "__main__":
    main()
