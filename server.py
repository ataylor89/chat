# This is a work in progress

import socket
import threading

# Packet types
CHAT_MESSAGE = 1

clients = {}

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = '127.0.0.1'
    port = 12345
    server_socket.bind((host, port))

    server_socket.listen()
    i = 0

    while True:
        client_socket, client_address = server_socket.accept()
        i += 1
        client_name = format("Client-%d" %i)
        clients[client_name] = (client_socket, client_address)
        thread = threading.Thread(target=readloop, args=(client_socket,client_name))
        thread.start()

def readloop(client_socket, client_name):
    done = False
    while not done:
        try:
            data = client_socket.recv(4)
            if len(data) < 4:
                continue
            packet_len = int.from_bytes(data, byteorder="big", signed=False)
            packet = data + client_socket.recv(packet_len-4)
            if len(packet) == packet_len:
                process(packet, client_name)
            else:
                print("The packet is shorter than the specified length")
        except socket.error as e:
            print(e)
            client_socket.close()
            del clients[clientname]
            done = True

def process(packet, client_name):
    packet_len = int.from_bytes(packet[0:4], byteorder="big", signed=False)
    packet_type = packet[4]
    if packet_type == CHAT_MESSAGE:
        message = format("%s: %s" %(client_name, packet[5:packet_len].decode("utf-8")))
        print(message)
        echo(message)

def echo(message):
    for client_name in clients:
        client_socket, client_address = clients[client_name]
        try:
            client_socket.sendall(message.encode("utf-8"))
        except socket.error as e:
            print(e)

if __name__ == "__main__":
    main()
