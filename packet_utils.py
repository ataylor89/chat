import packet_types

def hexdump(packet):
    packet_len = len(packet)
    index = 0
    contents = ''
    while index < packet_len:
        index_str = f'{index:0{7}x}:'
        words = []
        for i in range(0, 16, 2):
            word = ''
            if index + i + 1 < packet_len:
                value = packet[index+i+1]
                word += f'{value:0{2}x}'
            if index + i < packet_len:
                value = packet[index+i]
                word += f'{value:0{2}x}'
            else:
                break
            if len(word) > 0:
                words.append(word)
        line = format('%s %s\n' %(index_str, ' '.join(words)))
        contents += line
        index += 16
    return contents

def str(packet):
    packet_len = len(packet)
    packet_type = packet[4]
    packet_type = packet_types.map[packet_type] if packet_type in packet_types.map else 'UNKNOWN'
    packet_body = packet[5:packet_len].decode('utf-8')
    contents = format('Packet length: %d bytes\n' %packet_len)
    contents += format('Packet type: %s\n' %packet_type)
    contents += format('Packet body: %s' %packet_body)
    if not contents.endswith('\n'):
        contents += '\n'
    return contents
