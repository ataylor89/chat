import parser
import util
import sys

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

def main():
    if len(sys.argv) != 2:
        print("Usage: python decrypt.py <cipherfile>")
        sys.exit(0)
    cipherfile = open(sys.argv[1], "rb")
    ciphertext = cipherfile.read()
    ciphertext = ciphertext.decode("utf-8")
    key = parser.parse_key("privatekey.txt")
    msg = decrypt(ciphertext, key)
    print(msg, end='')

if __name__ == "__main__":
    main()
