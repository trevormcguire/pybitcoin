"""
Bitcoin's Hash Functions 
"""
from typing import *
import hashlib
from .ints import is_hex

def sha256(s: Union[str, bytes]) -> bytes:
    """
    ----------
    SHA256
    ----------
    Outputs 256 bits (32 bytes)
    ----------
    References
    ----------
        1. https://en.wikipedia.org/wiki/SHA-2
        2. https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf
        3. http://karpathy.github.io/2021/06/21/blockchain/ (for python implementation)
    
    """
    if isinstance(s, str):
        if is_hex(s):
            s = bytes.fromhex(s)
        else:
            s = s.encode()
    return hashlib.sha256(s).digest()

def hash256(s: Union[str, bytes]) -> bytes:
    """
    Hash256 == 2 rounds of SHA256
    """
    if isinstance(s, str):
        if is_hex(s):
            s = bytes.fromhex(s)
        else:
            s = s.encode()
    return sha256(sha256(s))


def hash160(s: Union[str, bytes]) -> bytes:
    """
    sha256 followed by ripemd160
    """
    if isinstance(s, str):
        if is_hex(s):
            s = bytes.fromhex(s)
        else:
            s = s.encode()
    return hashlib.new('ripemd160', sha256(s)).digest()
