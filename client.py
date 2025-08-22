# This is also a work in progress and eventually I will create a gui for the client

import socket
import threading
import time

host = '127.0.0.1'
port = 12345

def main():
    start_time = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    thread = threading.Thread(target=readloop, args=(s,))
    thread.start()
    while True:
        message = format("Time elapsed: %f seconds" %(time.time() - start_time))
        s.sendall(message.encode("utf-8"))
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
