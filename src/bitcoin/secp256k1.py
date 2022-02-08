"""
----------------
Paramters defining Bitcoin's Elliptic Curve are specified in secp256k1
----------------

Defines Bitcoin's curve (E) within Finite Field with prime (P)
y^2 = x^3 + ax + b

a = 0
b = 7

y^2 = x^3 + 7

The Generator Point (G) is the first point after infinity on the curve. 
Infinity (INF) functions as a 0 -- it is the point between which the Finite Field "wraps" back to the beginning.
If you begin with INF and add G, the result is G.
If you add G to the result, you get 2G. Add G again, you get 3G.
If you add G to itself a total of N times, you will be at INF once again.
So N (the order of G) represents how many distinct points are on the elliptic curve.
This also means that N represents how many private keys are possible -- which is why we can generate them with a random int between (1, N) 

----------------
Reference: https://en.bitcoin.it/wiki/Secp256k1
----------------
"""
from __future__ import annotations
from .ecc import Curve, Point


P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0x0000000000000000000000000000000000000000000000000000000000000000 # a = 0
B = 0x0000000000000000000000000000000000000000000000000000000000000007 # b = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141 #order of G


E = Curve(p=P, a=A, b=B)

G = Point(curve=E, x=Gx, y=Gy)

