def parse_key(path):
    key = []
    file = open(path, "r")
    for line in file:
        tokens = line.split()
        key.append((int(tokens[0][2:]), int(tokens[1][2:])))
    return key
