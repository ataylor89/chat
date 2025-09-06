from rsa import encrypt, decrypt, parser, util

def read_packet(s, key=None, encryption=False):
    if encryption:
        header = s.recv(5)
        if len(header) < 5:
            return None
        packet_len = int.from_bytes(header[0:4], byteorder="big", signed=False)
        body = s.recv(packet_len-5)
        if len(body) == packet_len-5:
            body = body.decode("utf-8")
            body = decrypt.decrypt(body, key)
            body = body.encode("utf-8")
            packet = header + body
            return packet
    else:
        header = s.recv(5)
        if len(header) < 5:
            return None
        packet_len = int.from_bytes(header[0:4], byteorder="big", signed=False)
        packet = header + s.recv(packet_len-5)
        if len(packet) == packet_len:
            return packet

def write_packet(s, packet_type, message, key=None, encryption=False):
    if encryption:
        body = message.encode("utf-8")
        body = body.decode("utf-8")
        body = encrypt.encrypt(body, key)
        body = body.encode("utf-8")
        packet_len = len(body) + 5
        header = packet_len.to_bytes(4, byteorder="big") + packet_type.to_bytes(1)
        packet = header + body
        s.sendall(packet)
    else:
        body = message.encode("utf-8")
        packet_len = len(body) + 5
        header = packet_len.to_bytes(4, byteorder="big") + packet_type.to_bytes(1)
        packet = header + body
        s.sendall(packet)
