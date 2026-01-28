from shared.rsa import util

def encrypt(msg, key):
    ciphertext = ''
    codepoints = list(map(lambda x: ord(x), msg))
    keylen = len(key)
    for i in range(len(codepoints)):
        (n, e) = key[i % keylen]
        size = util.size(n)
        cipher = util.power_mod_n(codepoints[i], e, n)
        encoding = util.encode(cipher, size)
        ciphertext += encoding
    return ciphertext
