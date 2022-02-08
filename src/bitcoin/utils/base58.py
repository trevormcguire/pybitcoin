"""
------------------------
BASE58
------------------------
Bitcoin has a home-made Base-58 encoding method

Base 58 uses all normal alphanumeric characters except for 0/O nad I/l because these pairs are easy to confuse 
    with each other.

Satoshi explained his/her rationale behind this encoding in the original source code (below comments were taken from there):
    // Why base-58 instead of standard base-64 encoding?
    // - Don't want 0OIl characters that look the same in some fonts and
    //      could be used to create visually identical looking account numbers.
    // - A string with non-alphanumeric characters is not as easily accepted as an account number.
    // - E-mail usually won't line-break if there's no punctuation to break at.
    // - Doubleclicking selects the whole number as one word if it's all alphanumeric.

This method is used to create wallet addresses and wallet imports.

For wallet addresses (P2PKH - Pay-to-pubkey-hash):
    > payload is RIPEMD160(SHA256(ECDSA_publicKey)), or more concisely hash160(pubkey)
    > where ECDSA_publicKey is a public key the wallet knows the private key for

For Wallet Import Format:
    > Procedure is the same, except it is 32 bytes instead of 20
    > This is because private key will be 32 bytes, while pubkey hash is 20 

------------------------
1. Wallet Import Format (WIF)
------------------------
    > Payload is 32 bytes
    > If compressed:
        1. Total of 38 bytes:
            i. Version (1 byte) + Payload (32 bytes) + Compression Flag (1 byte) + Checksum (4 bytes)
    > If uncompressed:
        1. Total of 37 bytes:
            i. Version (1 byte) + Payload (32 bytes) + Checksum (4 bytes)
------------------------
2. Addresses
------------------------
    > Total of 25 bytes
        i. Version (1 byte) + Payload (20 bytes) + Checksum (4 bytes)

------------------------
REFERENCE
------------------------
https://en.bitcoin.it/wiki/Wallet_import_format

https://en.bitcoin.it/wiki/Base58Check_encoding
------------------------
"""
from typing import *
from .hashfns import hash256

BASE58_CHARS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def encode(b: bytes) -> str:
    """
    ------------------------
    Encodes bytes as base58
    ------------------------
    """
    n_lead_zeros = len(b) - len(b.lstrip(b"\x00")) #find num of leading zeros
    n = int.from_bytes(b, "big") #get integer representation,
    res = ""
    while n > 0:
        n, mod = divmod(n, 58)
        res = BASE58_CHARS[mod] + res
    return "1" * n_lead_zeros + res

def decode(s: str, 
            payload_only: bool = True,
            wif: bool = False, 
            wif_compressed: bool = False) -> bytes:
    """
    Decodes Base 58, including if wallet import format (WIF)
    """
    if wif:
        num_bytes = 38 if wif_compressed else 37
    else:
        num_bytes = 25
    n = 0
    for c in s:
        n *= 58
        n += BASE58_CHARS.index(c)
    n = n.to_bytes(num_bytes, byteorder="big") 
    assert hash256(n[:-4])[:4] == n[-4:], "Checksum failed." #last 4 is checksum
    if payload_only:
        return n[1:-4]
    return n

def checksum(b: bytes):
    return hash256(b)[:4]


