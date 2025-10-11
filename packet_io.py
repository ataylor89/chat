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
                    log_message = format("%s -- %s\n" %(timestamp, "Received an encrypted packet"))
                    self.logger.write(log_message)
                    self.logger.write("Encrypted packet:\n")
                    contents = packet_utils.hexdump(encrypted_packet)
                    self.logger.write(contents)
                body = body.decode("utf-8")
                body = decrypt.decrypt(body, key)
                body = body.encode("utf-8")
                decrypted_packet = header + body
                if self.logging_enabled:
                    self.logger.write("Decrypted packet:\n")
                    contents = packet_utils.hexdump(decrypted_packet)
                    self.logger.write(contents)
                    contents = packet_utils.str(decrypted_packet)
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
                log_message = format("%s -- %s\n" %(timestamp, "Received an unencrypted packet"))
                self.logger.write(log_message)
                contents = packet_utils.hexdump(packet)
                self.logger.write("Unencrypted packet:\n")
                self.logger.write(contents)
                contents = packet_utils.str(packet)
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
                log_message = format("%s -- %s\n" %(timestamp, "Sent an encrypted packet"))
                self.logger.write(log_message)
                self.logger.write("Encrypted packet:\n")
                contents = packet_utils.hexdump(encrypted_packet)
                self.logger.write(contents)
                decrypted_packet = header + message.encode("utf-8") if message else header
                contents = packet_utils.hexdump(decrypted_packet)
                self.logger.write("Decrypted packet:\n")
                self.logger.write(contents)
                contents = packet_utils.str(decrypted_packet)
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
                log_message = format("%s -- %s\n" %(timestamp, "Sent an unencrypted packet"))
                self.logger.write(log_message)
                contents = packet_utils.hexdump(packet)
                self.logger.write("Unencrypted packet:\n")
                self.logger.write(contents)
                contents = packet_utils.str(packet)
                self.logger.write(contents)
                self.logger.write("\n")
                self.logger.flush()
