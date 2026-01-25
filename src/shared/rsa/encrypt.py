from shared.rsa import parser, util

def encrypt(msg, key):
    ciphertext = ""
    codes = msg.encode("utf-8")
    keylen = len(key)
    for i in range(0, len(codes)):
        (n, e) = key[i % keylen]
        size = util.size(n)
        cipher = util.power_mod_n(codes[i], e, n)
        encoding = util.encode(cipher, size)
        ciphertext += encoding
    return ciphertext
