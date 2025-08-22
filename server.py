import socket
import threading

clients = []

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = '127.0.0.1'
    port = 12345
    server_socket.bind((host, port))

    server_socket.listen()

    while True:
        client_socket, client_address = server_socket.accept()
        thread = threading.Thread(target=readloop, args=(client_socket,))
        clients.append(thread)
        thread.start()

def readloop(client_socket):
    data = client_socket.recv(1024)
    print("Received: %s" %data.decode("utf-8"))

if __name__ == "__main__":
    main()
