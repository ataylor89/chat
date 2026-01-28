from shared.exceptions import KeyFileError

def parse_key(path):
    keypair = {'public': [], 'private': []}
    with open(path, 'r') as file:
        for index, line in enumerate(file):
            linenum = index + 1
            try:
                tokens = line.split()
                n, e, d = int(tokens[0][2:]), int(tokens[1][2:]), int(tokens[2][2:])
                keypair['public'].append((n, e))
                keypair['private'].append((n, d))
            except ValueError as err:
                raise KeyFileError(f'Value could not be parsed as an integer in line {linenum} of key file')
            except IndexError as err:
                raise KeyFileError(f'Value missing in line {linenum} of key file')
    return keypair

def decode(str):
    key = []
    tokens = str.split(':')
    for token in tokens:
        parts = token.split(',')
        key.append((int(parts[0]), int(parts[1])))
    return key

def encode(key):
    tmp = []
    for k in key:
        str = format('%d,%d' %(k[0], k[1]))
        tmp.append(str)
    return ':'.join(tmp)
