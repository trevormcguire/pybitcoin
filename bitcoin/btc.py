from typing import *
from secp256k1 import Point256

class Bitcoin(object):
    """
    ----------------
    Object Representing a Bitcoin
    ----------------
    """
    def __init__(self, point: Point, n: int):
        self.point = point
        self.n = n 
        
