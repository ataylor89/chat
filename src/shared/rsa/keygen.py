import primetable
import keytable
import random
import argparse

def create_key_pair(keylen, tmin, tmax):
    keytable.load()
    filtered = {}
    for k,v in keytable.table.items():
        if v[1] >= tmin and v[1] <= tmax and v[2] >= tmin and v[2] <= tmax:
            filtered[k] = v
    if keylen > len(filtered):
        raise ValueError("There aren't enough keys in the key table that meet the criteria")
    nvalues = list(filtered.keys())
    nvalues = random.sample(nvalues, keylen)
    with open("publickey.txt", "w") as publickey, open("privatekey.txt", "w") as privatekey:
        for nvalue in nvalues:
            (n, p, q, phi, e, d) = filtered[nvalue]
            publickey.write("n=%d e=%d\n" %(n, e))
            privatekey.write("n=%d d=%d\n" %(n, d))

def main():
    primetable.load()
    parser = argparse.ArgumentParser(prog="keygen.py", description="Create a public key and a private key", epilog="Thanks for reading")
    parser.add_argument("-kl", "--keylength", type=int, required=True)
    parser.add_argument("-min", "--min_threshold", type=float, default=0)
    parser.add_argument("-max", "--max_threshold", type=float, default=primetable.get(-1))
    args = parser.parse_args()
    keylen = args.keylength
    tmin = int(args.min_threshold)
    tmax = int(args.max_threshold)
    try:
        create_key_pair(keylen, tmin, tmax)
    except Exception as err:
        print(err)
        return
    print("Created key pair in publickey.txt and privatekey.txt")
    
if __name__ == "__main__":
    main()
