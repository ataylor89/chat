import socket

host = '127.0.0.1'
port = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:
    socket.connect((host, port))
    message = "hello world"
    socket.sendall(message.encode("utf-8"))
    print("Sent: %s" %message)
