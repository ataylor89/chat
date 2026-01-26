def parse_key(path):
    key = {'public': [], 'private': []}
    file = open(path, "r")
    for line in file:
        tokens = line.split()
        key['public'].append((int(tokens[0][2:]), int(tokens[1][2:])))
        key['private'].append((int(tokens[0][2:]), int(tokens[2][2:])))
    return key

def decode(str):
    key = []
    tokens = str.split(":")
    for token in tokens:
        parts = token.split(",")
        key.append((int(parts[0]), int(parts[1])))
    return key

def encode(key):
    tmp = []
    for k in key:
        str = format("%d,%d" %(k[0], k[1]))
        tmp.append(str)
    return ":".join(tmp)
