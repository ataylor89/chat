class NetworkLog:
    def open(self, filename, mode):
        if hasattr(self, "file") and not self.file.closed:
            self.file.close()
        self.file = open(filename, mode)

    def close(self):
        if hasattr(self, "file") and not self.file.closed:
            self.file.close()

    def print(self, message=None):
        if message:
            self.file.write(message)
        self.file.write("\n")
        self.file.flush()

    def hexdump(self, packet):
        packet_len = len(packet)
        index = 0
        lines = []
        while index < packet_len:
            index_str = f"{index:0{7}x}:"
            words = []
            for i in range(0, 16, 2):
                word = ""
                if index + i + 1 < packet_len:
                    value = packet[index+i+1]
                    word += f"{value:0{2}x}"
                if index + i < packet_len:
                    value = packet[index+i]
                    word += f"{value:0{2}x}"
                else:
                    break
                if len(word) > 0:
                    words.append(word)
            line = format("%s %s" %(index_str, " ".join(words)))
            lines.append(line)
            index += 16
        dump = "\n".join(lines)
        self.file.write(dump)
        self.file.write("\n")
        self.file.flush()
