"""
Contains the base classes that include the math for Elliptic Curves over Finite Fields
"""
from __future__ import annotations
from typing import *
from .utils import modulardiv
from dataclasses import dataclass

class Curve(object):
    """
    -------------
    Object representing an Elliptic Curve, defined as:
        y^2 = x^3 + ax + b (mod p)
    -------------
    PARAMS:
        1. 'p' -> the prime  (Note this is optional if Elements are passed for a and b)
        2. 'a' -> coef
        3. 'b' -> coef
    """
    def __init__(self, p, a, b):
        self.p = p
        self.a = a
        self.b = b
    
    def __repr__(self):
        return f"EllipticCurve(a={self.a}, b={self.b}) in Field({self.p})"

@dataclass
class Point:
    """
    Object Representing a Point (x, y) along a curve
    """
    curve: Curve
    x: int
    y: int

    def __add__(self, other: Point) -> Point:
        """
        ------------------
        Point addition
        ------------------
            For an elliptic curve, a line will intersect either 1x or 3x (unless vertical or tangent)
                Adding two points is equivelent to the following:
                    1. draw a line through p1 and p2
                    2. extending that line until it intersects the curve again
                    3. Flip over x-axis
            Case1 -> self.x == p.x
                slope = (3*x1^2 + a) / 2y1
                x3 = s^2 - 2x1
                y3 = s(x1 - x3) - y1
            Case2 -> self.x != p.x
                slope = (y2 - y1) / (x2 - x1)
                x3 = s^2 - x1 - x2
                y3 = s(x1 - x3) - y1
            Case3 -> self == INF #identity fn
                return p
            Case4 -> p == INF #identity fn
                return self
            Case5 -> self.x == p.x and self.y != p.y #additive inverse -a + a = 0
                return INF
            Case6 -> self.x == p.x and self.y == 0 #line is tangent
                #this can only happen if P1 == P2 and P1.y and P2.y == 0
                return INF
        ------------------
        """
        prime = self.curve.p
        if self.x is None:
            return other
        if other.x is None:
            return self
        if self.x == other.x and self.y != other.y:
            return self.__class__(None, None, None) #INF
        
        if self.x == other.x: 
            m = modulardiv((3 * self.x**2 + self.curve.a), 
                           (2*self.y), 
                           prime)
        else:
            m = modulardiv((self.y - other.y), 
                           (self.x - other.x), 
                           prime)
        rx = (m**2 - self.x - other.x) % prime
        ry = (-(m*(rx - self.x) + self.y)) % prime
        return Point(self.curve, rx, ry)
    
    def __rmul__(self, n: int) -> Point:
        """
        Point Multiplication - Double And Add Algorithm
        https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication
        """
        curr = self
        res = self.__class__(self.curve, None, None) #point at infinity -- which you can think of as the point at which the field wraps back around
        while n:
            if n & 1:
                res += curr
            curr += curr
            n >>= 1 #right bitshift
        return res



INF = Point(None, None, None)

