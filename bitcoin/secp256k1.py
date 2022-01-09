from base import EllipCurve, Element, Point
from typing import *

class Element256(Element):
    """
    --------------------
    Represents an element in the set F(2^256 - 2^32 - 2^9 - 2^8 - 2^7 - 2^6 - 2^4 - 1)
    --------------------
    """
    def __init__(self, num: int, order=None):
        p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F 
        super().__init__(num, p)

    def __repr__(self):
        return f"secp256k1 Element({self.num}) in Finite Field({self.order})"

class Curve256(EllipCurve):
    """
    ------------------------------
    Represents secp256k1 -- Bitcoin's elliptic curve
    ------------------------------
    The curve E -> y^2 = x^3 + ax + b over Fp:
        a = 0
        b = 7
        y^2 = x^3 + 7
    Domain params are denoted by sextuple T = (p, a, b, G, n, h)
        p = FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE FFFFFC2F
            = 2^256 - 2^32 - 2^9 - 2^8 - 2^7 - 2^6 - 2^4 - 1
        Point G (compressed) = 02 79BE667E F9DCBBAC 55A06295 CE870B07 029BFCDB 2DCE28D9 59F2815B 16F81798
        Point G (uncompressed) = 04 79BE667E F9DCBBAC 55A06295 CE870B07 029BFCDB 2DCE28D9 
                                    59F2815B 16F81798 483ADA77 26A3C465 5DA4FBFC 0E1108A8 
                                    FD17B448 A6855419 9C47D08F FB10D4B8
        Point G = (0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798, 
                   0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)

        n (order of G) = FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE BAAEDCE6 AF48A03B BFD25E8C D0364141
        h (cofactor) = 01
    ---------------
    Reference: 
        https://en.bitcoin.it/wiki/Secp256k1
        http://www.secg.org/sec2-v2.pdf  page 9
    ---------------
    """
    def __init__(self):
        p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F 
        a = 0x0000000000000000000000000000000000000000000000000000000000000000
        b = 0x0000000000000000000000000000000000000000000000000000000000000007
        super().__init__(a=Element(a, p), b=Element(b, p), p=p)
    
    def __repr__(self):
        return f"secp256k1 Elliptic Curve(y^2 = x^3 + 7 in F(2^256 - 2^32 - 2^9 - 2^8 - 2^7 - 2^6 - 2^4 - 1)"


class Point256(Point):
    """
    --------------------
    Represents an (x, y) point along curve y^2 = x^3 + 7
    --------------------
    """
    def __init__(self, x: Union[int, Element], y: Union[int, Element]):
        assert type(x) == type(y) and type(x) in [int, Element], "'x' and 'y' must be the same data type (int or Element)"
        if isinstance(x, int):
            x, y = Element256(x), Element256(y)
        elif isinstance(x, Element):
            assert x.p == 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F, "Field order 'p' must follow secp256k1 specifications."
        curve = Curve256()
        super().__init__(x, y, curve)

    def __repr__(self) -> str:
        if self.x is None:
            return "secp256k1 Point(INF)"
        return f"secp256k1 Point({self.x.num}, {self.y.num}) along {self.curve}"

    def __rmul__(self, coef: int) -> Point:
        coef = coef % P #we can mod by p because pG = 0
        return super().__rmul__(coef)

#REFERENCE FOR BELOW CONSTANTS: https://en.bitcoin.it/wiki/Secp256k1

#P is the order of the finite field in which bitcoin operates
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F 

#G is the generating point 
G = Point256(
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
    )
    
#N is the order of G
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

#cofactor of the curve -- 1 means we are working on the entire curve (there is no subgroup) of order p
H = 1
