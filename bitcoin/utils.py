from random import randrange
from typing import *
from secp256k1 import N, G, Point256
from btc import Bitcoin

def generate_private_key() -> int:
    """
    Generates a random integer between 1 and N
    """
    return randrange(1, N)

def generate_public_key(private_key: int) -> Tuple[int]:
    """
    Generates a public key given a private key
    The public key is derived from the private key and Generating Point as follows:
        public key = private key * G
    """
    public_key = private_key * G
    return public_key.x.num, public_key.y.num

def generate_btc():
    """
    Generates a Bitcoin
    Reference:
        https://en.bitcoin.it/wiki/Secp256k1
    """
    return Bitcoin(G, N)
    