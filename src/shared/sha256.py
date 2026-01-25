import argparse

class SHA256Hash:
    def __init__(self, H1, H2, H3, H4, H5, H6, H7, H8):
        self.H1 = H1
        self.H2 = H2
        self.H3 = H3
        self.H4 = H4
        self.H5 = H5
        self.H6 = H6
        self.H7 = H7
        self.H8 = H8
        self.digest = (H1 << 224) + (H2 << 192) + (H3 << 160) + (H4 << 128) + (H5 << 96) + (H6 << 64) + (H7 << 32) + H8
        self.hexdigest = self.digest.to_bytes(32, 'big').hex()

K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

def pad(msg):
    bit_length = len(msg) * 8
    msg += bytes([0x80])
    while len(msg) % 64 != 56:
        msg += bytes([0])
    msg += bit_length.to_bytes(8, 'big')
    return msg

def mod32(x):
    return x & 0xFFFFFFFF

def ShR(x, n):
    return x >> n

def RotR(x, n):
    return mod32(x >> n | (x << (32 - n)))

def Ch(x, y, z):
    return (x & y) ^ (~x & z)

def Maj(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)

def S0(x):
    return RotR(x, 2) ^ RotR(x, 13) ^ RotR(x, 22)

def S1(x):
    return RotR(x, 6) ^ RotR(x, 11) ^ RotR(x, 25)

def s0(x):
    return RotR(x, 7) ^ RotR(x, 18) ^ ShR(x, 3)

def s1(x):
    return RotR(x, 17) ^ RotR(x, 19) ^ ShR(x, 10)

def sha256(msg):
    msg = pad(msg)
    H1 = 0x6a09e667
    H2 = 0xbb67ae85
    H3 = 0x3c6ef372
    H4 = 0xa54ff53a
    H5 = 0x510e527f
    H6 = 0x9b05688c
    H7 = 0x1f83d9ab
    H8 = 0x5be0cd19
    for i in range(len(msg)//64):
        W = []
        for j in range(64):
            if j < 16:
                offset = i * 64 + j * 4
                word = msg[offset: offset + 4]
                W.append(int.from_bytes(word, 'big'))
            else:
                result = s1(W[j - 2]) + W[j - 7] + s0(W[j - 15]) + W[j - 16]
                W.append(mod32(result))
        a, b, c, d, e, f, g, h = H1, H2, H3, H4, H5, H6, H7, H8
        for j in range(64):
            T1 = mod32(h + S1(e) + Ch(e, f, g) + K[j] + W[j])
            T2 = mod32(S0(a) + Maj(a, b, c))
            h = g
            g = f
            f = e
            e = mod32(d + T1)
            d = c
            c = b
            b = a
            a = mod32(T1 + T2)
        H1 = mod32(H1 + a)
        H2 = mod32(H2 + b)
        H3 = mod32(H3 + c)
        H4 = mod32(H4 + d)
        H5 = mod32(H5 + e)
        H6 = mod32(H6 + f)
        H7 = mod32(H7 + g)
        H8 = mod32(H8 + h)
    return SHA256Hash(H1, H2, H3, H4, H5, H6, H7, H8)
