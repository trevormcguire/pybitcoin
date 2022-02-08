from __future__ import annotations
from typing import *
from random import randint
from .ecc import Point
from .secp256k1 import G, P, N
from .utils import hash160, base58, modularsqrt

def randsk():
    return randint(1, N)

class PublicKey(Point):
    @classmethod
    def from_point(cls, pt: Point) -> PublicKey:
        """
        Point -> Public Key
        """ 
        return cls(pt.curve, pt.x, pt.y)
    
    @classmethod
    def from_private(cls, priv: int) -> PublicKey:
        """
        Public Keys can be generated from Private Keys by adding privkey to itself G times
        """
        return PublicKey.from_point(priv * G)

    def encode(self, compressed: bool = True, hash_160: bool = False) -> bytes:
        """
        SEC FORMAT
        """
        if compressed:
            prefix = b"\x02" if self.y % 2 == 0 else b"\x03" #2 if y is even else 3
            pubkey = prefix + self.x.to_bytes(32, "big")
        else:
            pubkey = b"\x04" + self.x.to_bytes(32, "big") + self.y.to_bytes(32, "big")
        if hash_160:
            return hash160(pubkey) #for the address generation
        return pubkey

    @classmethod
    def decode(cls, b: bytes):
        """
        Decode SEC formatted binary PublicKey
        - reversing the PublicKey.encode() method here
        """
        assert isinstance(b, bytes)
        curve = G.curve
        if b[0] == 4: #uncompressed
            x = int.from_bytes(b[1:33], 'big')
            y = int.from_bytes(b[33:65], 'big')
            return Point(curve, x, y)
        if b[0] in [2, 3]: #compressed -- need to reconstruct y by solving y^2 = x^3 + 7
            even = b[0] == 2
            x = int.from_bytes(b[1:], 'big')
            y2 = (pow(x, 3, P) + 7) % P
            y = modularsqrt(y2, P)
            y_even = y % 2 == 0
            if even != y_even: #ensure evenness is reflected
                y = P - y
            return cls(curve, x, y)
        raise ValueError("Bytes must be encoded in SEC Format")

    def get_address(self, compressed: bool, testnet: bool = True):
        pubkey_hash = self.encode(compressed=compressed, hash_160=True) #hash160 of SEC format
        prefix = b"\x6f" if testnet else b"\x00" #version
        address = prefix + pubkey_hash #version + pubkey hash
        checksum = base58.checksum(address) #get base58 checksum
        address += checksum 
        assert len(address) == 25, "Bytes must have length of 25" #version is 1 byte, hash is 20, checksum is 4
        return base58.encode(address) #return address encoded as base58



