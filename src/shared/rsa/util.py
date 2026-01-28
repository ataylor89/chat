def power_mod_n(base, expo, n):
    res = 1
    base = base % n
    while expo > 0:
        if expo & 1:
            res = (res * base) % n
        base = (base * base) % n
        expo = expo // 2
    return res

def encode(num, size):
    str = ''
    for i in range(0, size):
        str += chr(num & 0xFF)
        num = num >> 8
    return str

def decode(str):
    num = 0
    for i in range(0, len(str)):
        num += ord(str[i]) << 8*i
    return num

def size(num):
    k = 1
    while (2**8)**k - 1  < num:
        k += 1
    return k
