from rsa import encrypt, decrypt, parser, util
from network_log import NetworkLog
from datetime import datetime

class PacketIO:
    def __init__(self):
        self.logging_enabled = False

    def configure_log(self, filename, mode):
        self.logger = NetworkLog()
        self.logger.open(filename, mode)

    def enable_logging(self):
        self.logging_enabled = True

    def disable_logging(self):
        self.logging_enabled = False

    def read_packet(self, s, key=None, encryption=False):
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
                if self.logging_enabled:
                    message = format("%s -- %s" %(timestamp, "Received packet (original/encrypted)"))
                    self.logger.print(message)
                    self.logger.hexdump(encrypted_packet)
                    self.logger.print()
                body = body.decode("utf-8")
                body = decrypt.decrypt(body, key)
                body = body.encode("utf-8")
                decrypted_packet = header + body
                if self.logging_enabled:
                    message = format("%s -- %s" %(timestamp, "Received packet (processed/decrypted)"))
                    self.logger.print(message)
                    self.logger.hexdump(decrypted_packet)
                    self.logger.print()
                return decrypted_packet
        else:
            header = s.recv(5)
            if len(header) < 5:
                return None
            packet_len = int.from_bytes(header[0:4], byteorder="big", signed=False)
            packet = header + s.recv(packet_len-5)
            if self.logging_enabled:
                message = format("%s -- %s" %(timestamp, "Received packet (original/unencrypted)"))
                self.logger.print(message)
                self.logger.hexdump(packet)
                self.logger.print()
            if len(packet) == packet_len:
                return packet

    def write_packet(self, s, packet_type, message, key=None, encryption=False):
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
            if self.logging_enabled:
                message = format("%s -- %s" %(timestamp, "Sent packet (original/encrypted)"))
                self.logger.print(message)
                self.logger.hexdump(packet)
                self.logger.print()
        else:
            packet_len = 5
            if message:
                body = message.encode("utf-8")
                packet_len += len(body)
            header = packet_len.to_bytes(4, byteorder="big") + packet_type.to_bytes(1)
            packet = header + body if message else header
            s.sendall(packet)
            if self.logging_enabled:
                message = format("%s -- %s" %(timestamp, "Sent packet (original/unencrypted)"))
                self.logger.print(message)
                self.logger.hexdump(packet)
                self.logger.print()
