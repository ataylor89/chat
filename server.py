# This is a work in progress

import socket
import threading

clients = []

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = '127.0.0.1'
    port = 12345
    server_socket.bind((host, port))

    server_socket.listen()
    i = 0

    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        i += 1
        client_name = format("Client-%d" %i)
        thread = threading.Thread(target=readloop, args=(client_socket,client_name))
        thread.start()

def readloop(client_socket, client_name):
    done = False
    while not done:
        try:
            data = client_socket.recv(1024)
        except socket.error as e:
            print(e)
            client_socket.close()
            clients.remove(client_socket)
            done = True

        if len(data) == 0:
            continue

        message = format("%s: %s" %(client_name, data.decode("utf-8")))
        print(message)

        for client in clients:
            try:
                client.sendall(message.encode("utf-8"))
            except socket.error as e:
                print(e)
                client.close()
                clients.remove(client)

if __name__ == "__main__":
    main()
