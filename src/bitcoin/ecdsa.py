"""
-----------------
Utilities to work with the Elliptic Curve Digital Signature Algorithm (ECDSA)
-----------------
A signature is an tuple of two integers r and s
Note for (r,s):
    -----------------
    Let e = private key
    Let P = public key
    Let k = 256-bit random target
    Let R = (x, y) coords where r is x
    Let r = x coord of R
    Let z = signature hash
    -----------------
    u = z/s
    v = r/s

    eG = P

    kG = R = uG + vP
    vP = G(k - u)
    P = G((k-u)/v) = eG
    e = (k-u)/v
    k = u + ve = z/s + re/s = (z + re)/s
    s = (z + re)/k

-----------------
Verification
-----------------
    1. Input:
        > signature (r, s)
        > z (hash of the thing being signed)
        > P (public key of signer)
    2. Calculate u and v 
    3. Calculate R = uG + vP
    4. if R.x equals r, the signature is valid
-----------------
"""
from __future__ import annotations
from typing import *
from .secp256k1 import N, G
from .utils import modulardiv, ensure_stream, hash256
from .keys import PublicKey, randsk
import hashlib
import hmac


def rfc6979(sk: int, z: int) -> int:
    """
    ----------------
    Deterministic k Generation for signing from private as specified in RFC-6979:
        https://datatracker.ietf.org/doc/html/rfc6979
    ----------------
    The reason for this algorithm is to prevent a duplication of k across the network
        (see https://arstechnica.com/gaming/2010/12/ps3-hacked-through-poor-implementation-of-cryptography/)
    
    This is because no collisions have been found with SHA256 hashing algo yet
    ----------------
    """
    k = b"0x00" * 32
    v = b"0x01" * 32
    if z > N:
        z -= N
    z = z.to_bytes(32, "big")
    sk = sk.to_bytes(32, "big")
    for i in [b"\x00", b"\x01"]: #two rounds of sha256 (hash256) for added security 
        k = hmac.new(k, v + i + sk + z, hashlib.sha256).digest()
        v = hmac.new(k, v, hashlib.sha256).digest()

    while True:
        v = hmac.new(k, v, hashlib.sha256).digest()
        cand = int.from_bytes(v, "big")
        if 1 <= cand < N:
            return cand
        k = hmac.new(k, v+b"\x00", hashlib.sha256).digest()
        v = hmac.new(k, v, hashlib.sha256).digest()

def validate_signature(p: PublicKey, 
                       message: bytes, 
                       sig: Signature) -> bool:
    """
    Validates a signature given public key (p), message (z) and signature
    u, v = z/s, r/s
    R = uG + vp
    r = R.x
    assert r == sig.r
    """
    assert 1 <= sig.r <= N
    assert 1 <= sig.s <= N
    z = int.from_bytes(hash256(message), 'big') #the hash256 of the message (which is tx.encode(sig_idx))
    u = modulardiv(z, 
                   sig.s, N) #u = z/s
    v = modulardiv(sig.r, 
                   sig.s, N) #v = r/s
    R = (u * G) + (v * p)
    return R.x == sig.r

class Signature(object):
    """
    ----------------
    Object Representing a Signature
    ----------------
    PARAMS
    ----------------
        1. 'r' -> 256bit integer -> 32bytes big-endian unless first byte if > 0x80 (33bytes)
        2. 's' -> 256bit integer -> 32bytes big-endian unless first byte if > 0x80 (33bytes)
    ----------------
    """
    def __init__(self, r, s):
        self.r = r
        self.s = s
    
    def __repr__(self):
        return f"Signature(r:{self.r}\ns:{self.s})"
            
    @classmethod
    def from_private(cls, sk: int, z: int, randk: bool = False) -> Signature:
        """
        Generates a signature given a secret key and a "message"
        sk is the secret/private key
        z is the hash256 of an encoded Tx - hash256(tx.encode(sig_idx=0))
        """
        k = randsk() if randk else rfc6979(sk, z)
        r = (k*G).x #r is the x coord of R = kG
        s = modulardiv((z + r * sk), k, N)
        if s > N/2: #a low s will get nodes to relay transactions
            s = N - s
        return Signature(r, s)

    def encode(self) -> bytes:
        """
        ----------------
        > Distinguished Encoding Rules (DER) Format
        > Needs to encode both r and s
        > Cannot be compressed because s can't be derived from r
        ----------------
        Serialization Procedure (DER)
        ----------------
            1. Start with 0x30 byte
            2. Encode length of rest of sig (usually 0x44 or 0x45)
            3. Append marker byte 0x02
            4. Encode r as big-endian
                a. Prepend with 0x00 if r's first byte is > 0x80
                b. Prepend resulting length of r
            5. Append marker 0x02
            6. Encode s as big-endian
                a. Prepend 0x00 if first byte > 0x80
                b. Preprend resulting length to s
        ----------------
        """
        rbin = self.r.to_bytes(32, "big")
        rbin = rbin.lstrip(b"\x00") #remove null bytes 
        sbin = self.s.to_bytes(32, "big")
        sbin = sbin.lstrip(b"\x00")

        if rbin[0] >= 0x80:
            rbin = b"\x00" + rbin
        if sbin[0] >= 0x80:
            sbin = b"\x00" + sbin

        res = b"".join([bytes([0x02, len(rbin)]), rbin, bytes([0x02, len(sbin)]), sbin])
        return b"".join([bytes([0x30, len(res)]), res])

    @classmethod
    def decode(cls, sig_bytes: bytes):
        """
        Decodes DER Formatted binary Signature
        - just reverseing Signature.encode() method here
        - dont forget about the sighash b"\x01" we added!
        """
        b = ensure_stream(sig_bytes)
        assert b.read(1)[0] == 0x30
        length = b.read(1)[0]
        assert length == len(sig_bytes) - 3 # -3 excludes the starting 0x30, length, sighash
        assert b.read(1)[0] == 0x02
        rlength = b.read(1)[0]
        r = int.from_bytes(b.read(rlength), 'big')
        assert b.read(1)[0] == 0x02
        slength = b.read(1)[0]
        s = int.from_bytes(b.read(slength), 'big')
        assert len(sig_bytes) == 7 + rlength + slength # 7 is metadata + sighash
        return cls(r, s)


