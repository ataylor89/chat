from rsa import encrypt, decrypt, parser, util
from network_log import NetworkLog
from datetime import datetime

logger = NetworkLog()

def configure_log(filename, mode):
    logger.open(filename, mode)

def read_packet(s, key=None, encryption=False, log=False):
    now = datetime.now().astimezone()
    timestamp = now.strftime("%m/%d/%Y %-I:%M.%f %p %Z")
    if encryption:
        header = s.recv(5)
        if len(header) < 5:
            return None
        packet_len = int.from_bytes(header[0:4], byteorder="big", signed=False)
        body = s.recv(packet_len-5)
        encrypted_packet = header + body
        if len(encrypted_packet) == packet_len:
            if log:
                message = format("%s -- %s" %(timestamp, "Received packet (original/encrypted)"))
                logger.print(message)
                logger.hexdump(encrypted_packet)
                logger.print()
            body = body.decode("utf-8")
            body = decrypt.decrypt(body, key)
            body = body.encode("utf-8")
            decrypted_packet = header + body
            if log:
                message = format("%s -- %s" %(timestamp, "Received packet (processed/decrypted)"))
                logger.print(message)
                logger.hexdump(decrypted_packet)
                logger.print()
            return decrypted_packet
    else:
        header = s.recv(5)
        if len(header) < 5:
            return None
        packet_len = int.from_bytes(header[0:4], byteorder="big", signed=False)
        packet = header + s.recv(packet_len-5)
        if log:
            message = format("%s -- %s" %(timestamp, "Received packet (original/unencrypted)"))
            logger.print(message)
            logger.hexdump(packet)
            logger.print()
        if len(packet) == packet_len:
            return packet

def write_packet(s, packet_type, message, key=None, encryption=False, log=False):
    now = datetime.now().astimezone()
    timestamp = now.strftime("%m/%d/%Y %-I:%M.%f %p %Z")
    if encryption:
        packet_len = 5
        if message:
            body = encrypt.encrypt(message, key)
            body = body.encode("utf-8")
            packet_len += len(body)
        header = packet_len.to_bytes(4, byteorder="big") + packet_type.to_bytes(1)
        packet = header + body if message else header
        s.sendall(packet)
        if log:
            message = format("%s -- %s" %(timestamp, "Sent packet (original/encrypted)"))
            logger.print(message)
            logger.hexdump(packet)
            logger.print()
    else:
        packet_len = 5
        if message:
            body = message.encode("utf-8")
            packet_len += len(body)
        header = packet_len.to_bytes(4, byteorder="big") + packet_type.to_bytes(1)
        packet = header + body if message else header
        s.sendall(packet)
        if log:
            message = format("%s -- %s" %(timestamp, "Sent packet (original/unencrypted)"))
            logger.print(message)
            logger.hexdump(packet)
            logger.print()
