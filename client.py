# This is also a work in progress and eventually I will create a gui for the client

import socket
import threading
import time
from datetime import datetime

# Packet types
CHAT_MESSAGE = 1

host = '127.0.0.1'
port = 12345

def main():
    start_time = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    thread = threading.Thread(target=readloop, args=(s,))
    thread.start()
    while True:
        message = format("The time is %s" %datetime.now().strftime("%I:%M:%S %p"))
        packet_len = len(message) + 5
        packet = packet_len.to_bytes(4, byteorder="big")
        packet_type = 1
        packet += packet_type.to_bytes(1)
        packet += message.encode("utf-8")
        s.sendall(packet)
        time.sleep(60)

def readloop(s):
    done = False
    while not done:
        try:
            data = s.recv(1024)
            if len(data) > 0:
                print(data.decode("utf-8"))
        except socket.error as e:
            print(e)
            s.close()
            done = True

if __name__ == "__main__":
    main()
