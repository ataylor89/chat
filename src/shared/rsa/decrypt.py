from shared.rsa import parser, util

def decrypt(ciphertext, key):
    message = ""
    keylen = len(key)
    start = 0
    end = 0
    i = 0
    while start < len(ciphertext):
        (n, d) = key[i % keylen]
        size = util.size(n)
        end = start + size
        substr = ciphertext[start:end]
        cipher = util.decode(substr)
        message += chr(util.power_mod_n(cipher, d, n))
        i += 1
        start += size
    return message
