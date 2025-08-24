import parser
import util
import sys

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

def main():
    if len(sys.argv) != 2: 
        print("Usage: python encrypt.py <messagefile>")
        sys.exit(0)
    msgfile = open(sys.argv[1], "r")
    msg = msgfile.read()
    key = parser.parse_key("publickey.txt")
    ciphertext = encrypt(msg, key)
    print(ciphertext, end='')

if __name__ == "__main__":
    main()
