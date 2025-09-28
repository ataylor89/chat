import packet_utils
from rsa import encrypt, decrypt, parser, util
from datetime import datetime

class PacketIO:
    def __init__(self):
        self.logger = None
        self.logging_enabled = False

    def configure_log(self, filename, mode):
        if self.logger and not self.logger.closed:
            self.logger.close()
        self.logger = open(filename, mode)

    def close_log(self):
        if self.logger and not self.logger.closed:
            self.logger.close()

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
                    log_message = format("%s -- %s\n" %(timestamp, "Received packet (original/encrypted)"))
                    self.logger.write(log_message)
                    contents = packet_utils.hexdump(encrypted_packet)
                    self.logger.write(contents)
                    self.logger.write("\n")
                    self.logger.flush()
                body = body.decode("utf-8")
                body = decrypt.decrypt(body, key)
                body = body.encode("utf-8")
                decrypted_packet = header + body
                if self.logging_enabled:
                    log_message = format("%s -- %s\n" %(timestamp, "Received packet (processed/decrypted)"))
                    self.logger.write(log_message)
                    contents = packet_utils.hexdump(decrypted_packet)
                    self.logger.write(contents)
                    self.logger.write("\n")
                    self.logger.flush()
                return decrypted_packet
        else:
            header = s.recv(5)
            if len(header) < 5:
                return None
            packet_len = int.from_bytes(header[0:4], byteorder="big", signed=False)
            packet = header + s.recv(packet_len-5)
            if self.logging_enabled:
                log_message = format("%s -- %s\n" %(timestamp, "Received packet (original/unencrypted)"))
                self.logger.write(log_message)
                contents = packet_utils.hexdump(packet)
                self.logger.write(contents)
                self.logger.write("\n")
                self.logger.flush()
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
            encrypted_packet = header + body if message else header
            s.sendall(encrypted_packet)
            if self.logging_enabled:
                log_message = format("%s -- %s\n" %(timestamp, "Sent packet (original/encrypted)"))
                self.logger.write(log_message)
                contents = packet_utils.hexdump(encrypted_packet)
                self.logger.write(contents)
                self.logger.write("\n")
                self.logger.flush()
                log_message = format("%s -- %s\n" %(timestamp, "Sent packet (processed/decrypted)"))
                self.logger.write(log_message)
                decrypted_packet = header + message.encode("utf-8")
                contents = packet_utils.hexdump(decrypted_packet)
                self.logger.write(contents)
                self.logger.write("\n")
                self.logger.flush()
        else:
            packet_len = 5
            if message:
                body = message.encode("utf-8")
                packet_len += len(body)
            header = packet_len.to_bytes(4, byteorder="big") + packet_type.to_bytes(1)
            packet = header + body if message else header
            s.sendall(packet)
            if self.logging_enabled:
                log_message = format("%s -- %s\n" %(timestamp, "Sent packet (original/unencrypted)"))
                self.logger.write(log_message)
                contents = packet_utils.hexdump(packet)
                self.logger.write(contents)
                self.logger.write("\n")
                self.logger.flush()
