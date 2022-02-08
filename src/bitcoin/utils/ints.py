"""
Integer Handling for Bitcoin
"""
from typing import *
from io import BytesIO
from random import randint

def modulardiv(a, b, p):
    """
    --------------
    Modular Multiplicative Inverse
    --------------
    """
    return (a * pow(b, p-2, p)) % p

def modularsqrt(x, p):
    """
    --------------
    Modular Square Root of (x) with prime (p)
    --------------
    """
    return pow(x, (p+1)//4, p)
    
def is_hex(s: str) -> bool:
    """
    Hack way to show if a string is a hexadecimal -- works for our purposes here
    """
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def ensure_stream(b: Union[bytes, BytesIO]) -> BytesIO:
    assert type(b) in [bytes, BytesIO], "Input must be bytes."
    if isinstance(b, bytes):
        return BytesIO(b)
    return b

def encode_int(i: int, num_bytes: int, encoding: str = "little") -> bytes:
    """
    Encodes an integer into num bytes based on big or little endian
    """
    return i.to_bytes(num_bytes, encoding)

def decode_int(s: Union[BytesIO, bytes], nbytes: int, encoding: str = "little") -> int:
    s = ensure_stream(s)
    return int.from_bytes(s.read(nbytes), encoding)

def encode_varint(i: int) -> bytes:
    """
    Encode a very large integer into bytes with by compressing it with the following schema
    """
    if i < 0xfd: #253
        return bytes([i])
    elif i < 0x10000: #65536
        return b"\xfd" + encode_int(i, 2)
    elif i < 0x100000000: #4294967296
        return b"\xfe" + encode_int(i, 4) 
    elif i < 0x10000000000000000: #8446744073709551616
        return b"\xff" + encode_int(i, 8)
    else:
        raise ValueError("Integer is too large") 

def decode_varint(s: bytes) ->int:
    i = decode_int(s, 1)
    if i == 0xfd:
        return decode_int(s, 2)
    elif i == 0xfe:
        return decode_int(s, 4)
    elif i == 0xff:
        return decode_int(s, 8)
    else:
        return i
    