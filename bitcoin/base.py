from __future__ import annotations
from typing import *


class Element(object):
    """
    ----------------
    Represents an element within a finite field
    ----------------
    PARAMS
        1. num -> element in the set F(p)
        2. order -> size of the set (p)
    ----------------
    [Description]
        1. Finite Set -> {0, 1, 2,...,p-1} where p is the order of the set
        2. Element (this class) is a point within the finite field.
    ----------------
    [Finite Field Characteristics]
        1. Closed -> if a and b in F, then a + b and a * b in F
        2. Additive and Multiplicative Identity functions exist
            a. Additive (0 exists and a + 0 = a)
            b. Multiplicative (1 exists and a * 1 = a)
        3. Additive and Multiplicative inverses exist
            a. Additive (a + -a = 0)
            b. Multiplicative (a * a^-1 = 1) -> if a != 0
        4. Follows Modulo Arithmetic

        Reference: Programming Bitcoin, Jimmy Song
    ----------------
    """
    def __init__(self, num: int, order: int):
        assert num >= 0, f"'num' ({num}) must be greater than or equal to 0"
        assert num < order, f"'num' ({num}) must be less than 'order'"
        self.num = num
        self.order = order
    
    def __repr__(self) -> str:
        return f"Element({self.num}) in Finite Field({self.order})"
    
    def __eq__(self, ele: Element) -> bool:
        if ele:
            return self.num == ele.num and self.order == ele.order
        return False

    def __ne__(self, ele: Element) -> bool:
        return not self == ele
    
    def __add__(self, ele: Union[Element, int]) -> Element:
        """
        a + b = (a + b) % p
        """
        ele = self.__ensure_type(ele)
        self.__ensure_same_order(ele)
        return self.__class__(num=(self.num + ele.num) % self.order, order=self.order)

    def __sub__(self, ele: Union[Element, int]) -> Element:
        """
        a - b = (a - b) % p
        """
        ele = self.__ensure_type(ele)
        self.__ensure_same_order(ele)
        return self.__class__(num=(self.num - ele.num) % self.order, order=self.order)

    def __mul__(self, ele: Union[Element, int]) -> Element:
        """
        a * b = (a * b) % p
        """
        ele = self.__ensure_type(ele)
        self.__ensure_same_order(ele)
        return self.__class__(num=(self.num * ele.num) % self.order, order=self.order)
    
    def __rmul__(self, coef: int) -> Element:
        return self.__class__(num=(self.num * coef) % self.order, order=self.order)

    def __pow__(self, exp: int) -> Element:
        """
        ---------------
        To deal with negative exponents, we need to force the exp into range (0, p-2)
            - we can do this by adding p to the exp until its positive
            - exp % p-1 does the same thing but faster
        ---------------
        a^exp = a^exp % p
        """
        exp = exp % (self.order - 1) #forces the exponent into range (0, p-2)
        return self.__class__(num=pow(self.num, exp, self.order), order=self.order)

    def __truediv__(self, ele: Union[Element, int]) -> Element:
        """
        ---------------
        Fermat's Little Theorem
            > a^p-1 % p = 1
            > 1/n = n^p-2 % p
            Ref: https://en.wikipedia.org/wiki/Fermat%27s_little_theorem
        ---------------
        a / b = (a * b^p-2 % p) % p
        """
        ele = self.__ensure_type(ele)
        self.__ensure_same_order(ele)
        res = (self.num * pow(ele.num, self.order - 2, self.order)) % self.order
        return self.__class__(res, self.order)
    
    def __ensure_same_order(self, ele: Element) -> bool:
        assert self.order == ele.order, "Both Field Elements must have the same order."
    
    def __ensure_type(self, n: int) -> Element:
        if isinstance(n, int):
            return self.__class__(n, self.order)
        return n

class EllipCurve(object):
    """
    ------------------------------
    Represents an elliptic curve
    ------------------------------
    Elliptic Curves have the form y^2 = x^3 + ax + b
        Note: y^2 causes the graph to be symmetric over the x-axis
    ------------------------------
    ---------------
    """
    def __init__(self, a: Union[Element, int], b: Union[Element, int], p: int = None):
        assert type(a) == type(b), f"'a' and 'b' must be the same data type (either int or Element). You passed {a} and {b}"
        if isinstance(a, Element):
            assert a.order == b.order, f"{a} and {b} must have the same order"
            self.p = a.order
        else:
            assert isinstance(p, int), "If passing integer types into 'a' and 'b', you must specify field size 'p'."
            self.p = p
        self.a = a
        self.b = b
        

    def __repr__(self):
        m = self.a.num if isinstance(self.a, Element) else self.a
        b = self.b.num if isinstance(self.b, Element) else self.b
        eq = f"y^2 = x^3 + {m}x + {b}"
        return f"Elliptic Curve({eq} in F({self.p})"


class Point(object):
    """
    ---------------
    Represents a point (x, y) along an elliptic curve
    ---------------
    """
    def __init__(self, x: Union[Element, int], y: Union[Element, int], curve: EllipCurve):
        self.x = x if isinstance(x, Element) or not x else Element(x, curve.p)
        self.y = y if isinstance(y, Element) or not y else Element(y, curve.p)
        self.curve = curve
        if self.x and self.y:
            self.__assert_oncurve()

    def __assert_oncurve(self):
        """
        Any:
            y^2 = x^3 + ax + b
            0 = (y^2 - x^3 - ax - b) % p 
        Shorthand for Bitcoin:
            y^2 = x^3 + 7
            0 = (y^2 - x^3 - 7) % p
            assert (self.y**2 - self.x**3 - 7) % self.curve.p == 0, "Point is not along the curve defined by y^2 = x^3 + 7 (secp256k1)"
        """
        err = f"Point {self} is not along the curve y^2 = x^3 + 0x + 7 (y^2 = x^3 + {self.curve.a}x + {self.curve.b}"
        if isinstance(self.x, Element):
            assert self.y**2 - self.x**3 - (self.curve.a * self.x) - self.curve.b == Element(0, self.curve.p), err
        #assert (self.y**2 - self.x**3 - (self.curve.a * self.x) - self.curve.b) % self.curve.p == 0, err

    def __repr__(self) -> str:
        if self.x is None:
            return "Point(INF)"
        return f"Point({self.x.num}, {self.y.num}) along {self.curve}"

    def __eq__(self, p: Point) -> bool:
        return self.x == p.x and self.y == p.y and self.curve.a == p.curve.a and self.curve.b == p.curve.b
    
    def __ne__(self, p: Point) -> bool:
        return not self == p
    
    def __add__(self, p: Point) -> Point:
        """
        Point addition
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
        """
        self.__assert_same_curve(p)
        #Cases 3 and 4 -- identity (point + 0 = 0)
        if self == INF: 
            return p
        elif p == INF:
            return self
        if self.x == p.x:
            if self.y != p.y or self.y == 0: #cases 5 and 6
                return INF
            #Case 1 -> self == p and y > 0
            m = (3 * self.x**2 + self.curve.a) / (2 * self.y)
            res_x = m**2 - 2 * self.x
            res_y = m * (self.x - res_x) - self.y
            return Point(res_x, res_y, self.curve)
        else: 
            #Case 2 -> self.x != p.x
            m = (p.y - self.y) / (p.x - self.x)
            res_x = m**2 - self.x - p.x
            res_y = m * (self.x - res_x) - self.y 
            return Point(res_x, res_y, self.curve)

    def __rmul__(self, coef: int) -> Point:
        """
        Double until we are past how large the coefficient can be
        7 * Point
        """
        assert coef >= 0 and isinstance(coef, int), f"'coef' must be a positive integer. You passed: {coef}"
        res = INF
        curr = self
        while coef:
            if coef & 1: #check if rightmost bit is a 1
                res += curr
            curr += curr
            coef >>= 1 #bit shift to the right
        return res

    def __assert_same_curve(self, p: Point):
        assert self.curve.a == p.curve.a and self.curve.b == p.curve.b, f"Points {self} and {p} are not on same curve."




INF = Point(None, None, None) #obect representing infinity -- the "identity point"
