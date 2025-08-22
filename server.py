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
        clients.append(client_socket)
        thread.start()

def readloop(client_socket):
    done = False
    while not done:
        try:
            data = client_socket.recv(1024)
        except socker.error as e:
            print(e)
            client_socket.close()
            clients.remove(client_socket)
            done = True

        if len(data) == 0:
            continue

        print("Received: %s" %data.decode("utf-8"))

        for client in clients:
            if client == client_socket:
                continue
            try:
                client.sendall(data)
            except socket.error as e:
                print(e)
                client.close()
                clients.remove(client)

if __name__ == "__main__":
    main()
