def read_packet(s):
    header = s.recv(4)
    if len(header) < 4:
        return None
    packet_len = int.from_bytes(header, byteorder="big", signed=False)
    packet = header + s.recv(packet_len-4)
    if len(packet) == packet_len:
        return packet

def write_packet(s, packet_type, message):
    body = packet_type.to_bytes(1) + message.encode("utf-8")
    packet_len = len(body) + 4
    header = packet_len.to_bytes(4, byteorder="big")
    packet = header + body
    s.sendall(packet)
