def hexdump(packet):
    packet_len = len(packet)
    index = 0
    contents = ""
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
        line = format("%s %s\n" %(index_str, " ".join(words)))
        contents += line
        index += 16
    return contents
