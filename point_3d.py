from math import fmod, cos, sin, sqrt, asin, acos
from random import random


#  dwh coordinates
#
#  h
#  ^
#  |    d
#  |   /|
#  |  /
#  | /
#  |/
# -+-----------> w
# /|
#
# Descartes (cartesian) coordinates:
# d: distance aka X-isometric, positive - away
# w: width aka Y-horizontal, positive -  to right
# h: height aka Z-vertical, positive - up
#
# Important!: d/w/h is the left coordinated. I.e. counterpart to the standard (right) mathematical x/y/z (x - to to,
# y - to right, z - to top). This choice is to have clockwise d/w angle.
#
# Polar coordinates:
# r: radius, r >= 0
# a: azimuth - d/w angle, clockwise counter-corkscrew, d-direction is 0°
# e: elevation - (dw)/h, is counterclockwise, dw-plain is 0°, -pi/2 (-90°) .. +pi/2 (+90°)
#
#  d = r*cos(e)*cos(a);
#  w = r*cos(e)*sin(a);
#  h = r*sin(e)
#

class Point_3D:
    def __init__(self, d, w, h):
        self.d = d  # distance aka X-isometric, positive - away
        self.w = w  # width aka Y-horizontal, positive -  to right
        self.h = h  # height aka Z-vertical, positive - up

    def print(self, msg=None):
        if msg is None:
            print("3d point: (d={0:.3f}, w={1:.3f}, h={2:.3f})".format(self.d, self.w, self.h))
        else:
            print("{0}: (d={1:.3f}, w={2:.3f}, h={3:.3f})".format(msg, self.d, self.w, self.h))

    def move_to(self, d, w, h):
        self.d = d
        self.w = w
        self.h = h

    def move_to_point_3d(self, p):
        self.d = p.d
        self.w = p.w
        self.h = p.h

    def move_to_point_3d_polar(self, p_polar):
        p = p_polar.point_3d()
        self.d = p.d
        self.w = p.w
        self.h = p.h

    def point_3d_polar(self):  # -> Point_3D_Polar
        return Point_3D_Polar(0, 0, 0).move_to_point_3d(self)
        pass

    def add(self, x):
        return Point_3D(self.d+x.d, self.w+x.w, self.h+x.h)

    def sub(self, x):
        return Point_3D(self.d-x.d, self.w-x.w, self.h-x.h)

    def mul(self, x):
        return Point_3D(self.d*x.d, self.w*x.w, self.h*x.h)

    def div(self, x):
        return Point_3D(self.d/x.d, self.w/x.w, self.h/x.h)

    def scale(self, x: float):
        return Point_3D(self.d*x, self.w*x, self.h*x)

    def random(self):
        return Point_3D(self.d*random(), self.w*random(), self.h*random())


class Const:
    pi = 3.14159
    half_pi = pi/2
    three_half_pi = 3*pi/2
    two_pi = 2*pi
    minus_pi = -pi
    minus_half_pi = -pi/2
    rad_to_grad = 180/pi
    grad_to_rad = pi/180


class Point_3D_Polar:
    def __init__(self, radius=0.0, azimuth=0.0, elevation=0.0):
        self.r = radius     # radius, keep always positive
        self.a = azimuth    # azimuth, rad, keep between 0..+2*pi(360°), clockwise
        self.e = elevation  # elevation, rad (NOT! inclination), keep between -/+pi/2 (90°), counterclockwise
        self.fix()

    def fix(self):
        # keep r always positive
        if self.r < 0:
            self.r = -self.r
            self.a = self.a + Const.pi
            self.e = -self.e
        # keep e between [-pi/2 (-90°) .. +pi/2 (+90°)]
        self.e = fmod(self.e, Const.two_pi)   # e is in (-2*pi, +2*pi) after that
        if self.e < 0:
            self.e += Const.two_pi            # e is in [0, +2*pi) after that
        if self.e <= Const.half_pi:           # nothing to do
            pass
        elif self.e <= Const.pi:
            self.e = Const.pi - self.e
            self.a = self.a + Const.pi
        elif self.e <= Const.three_half_pi:
            self.e = Const.pi - self.e
            self.a = self.a + Const.pi
        else:  # self.e <= Const.two_pi:
            self.e = self.e - Const.two_pi
        # keep a between [0 .. +2*pi (+360°))
        self.a = fmod(self.a, Const.two_pi)
        if self.a < 0:
            self.a += Const.two_pi

    def print(self, msg=None):
        if msg is None:
            print("3d point polar: r={0:.3f}, a={1:6.2f}° ({2:+6.4}), e={3:6.2f}° ({4:+6.4})".format(
                self.r, self.a*Const.rad_to_grad, self.a, self.e*Const.rad_to_grad, self.e
            ))
        else:
            print("{0}: r={1:.3f}, a={2:6.2f}° ({3:+6.4}), e={4:6.2f}° ({5:+6.4})".format(
                msg, self.r, self.a*Const.rad_to_grad, self.a, self.e*Const.rad_to_grad, self.e
            ))

    def move_to(self, r, a, e):
        self.r = r
        self.a = a
        self.e = e

    def move_to_point_3d(self, p: Point_3D):
        dw2 = p.d*p.d+p.w*p.w
        dw = sqrt(dw2)
        r2 = dw2+p.h*p.h
        r = sqrt(r2)
        self.r = r
        if dw == 0:  # covers r==0 as well
            if p.h < 0.0:
                self.e = Const.minus_half_pi
            elif p.h > 0.0:
                self.e = Const.half_pi
            else:  # covers r==0
                self.e = 0.0
            self.a = 0.0
            return self
        else:  # covers r != 0 and d != 0 :
            self.e = asin(p.h/r)
            self.a = acos(p.d/dw)  # acos() is in [0, pi]
            if p.w < 0:
                self.a = Const.two_pi - self.a
            return self

    def move_to_point_3d_polar(self, p_polar):
        self.r = p_polar.r
        self.a = p_polar.a
        self.e = p_polar.e

    def point_3d(self) -> Point_3D:
        d = self.r*cos(self.e)*cos(self.a)
        w = self.r*cos(self.e)*sin(self.a)
        h = self.r*sin(self.e)
        return Point_3D(d, w, h)

    def add(self, x):
        return Point_3D_Polar(self.r+x.r, self.a+x.a, self.e+x.e)

    def sub(self, x):
        return Point_3D_Polar(self.a-x.a, self.a-x.a, self.e-x.e)

    def scale(self, x: float):
        return Point_3D_Polar(self.a*x, self.a, self.e)

    def random(self):
        return Point_3D_Polar(self.a*random(), Const.two_pi*random(), Const.pi*random()-Const.half_pi)


def grad(rad: float):
    return rad*Const.rad_to_grad
    pass


def rad(grad: float):
    return grad*Const.grad_to_rad
    pass


if __name__ == "__main__":

    center = Point_3D(250, 125, 125)
    center.print("AAA")
    print()

    for a in [rad(+10), rad(+90+10), rad(+180+10), rad(+270+10), rad(+360+10),
              rad(-10), rad(-90-10), rad(-180-10), rad(-270-10), rad(-360-10)]:
        for e in [rad(+10), rad(+90+10), rad(+180+10), rad(+270+10), rad(+360+10),
                  rad(-10), rad(-90-10), rad(-180-10), rad(-270-10), rad(-360-10)]:
            print("Step a={0:.0f}, e={1:.0f}".format(grad(a), grad(e)))
            center1 = Point_3D_Polar(10, a, e)
            center1.print("BBB1")
            center2 = Point_3D_Polar(0, 0, 0).move_to_point_3d(Point_3D(10*cos(e)*cos(a), 10*cos(e)*sin(a), 10*sin(e)))
            center2.print("BBB2")

    print()

    center = Point_3D_Polar(1, rad(+45), rad(+45))
    center.point_3d().print("CCC+++")
    center = Point_3D_Polar(-1, rad(+180+45), rad(-45))
    center.point_3d().print("CCC+++")
    center = Point_3D_Polar(1, rad(+180+45), rad(-45))
    center.point_3d().print("CCC---")
    center = Point_3D_Polar(-1, rad(+45), rad(+45))
    center.point_3d().print("CCC---")
    center = Point_3D_Polar(1, rad(+45), rad(-45))
    center.point_3d().print("CCC++-")
    center = Point_3D_Polar(1, rad(360-45), rad(+45))
    center.point_3d().print("CCC+-+")
    print()

    x = Point_3D_Polar(0, 0, 0)
    x.move_to_point_3d(Point_3D(1, 1, 1))
    x.print("EEE")
    x.point_3d().print("DDD+++")
    x.move_to_point_3d(Point_3D(-1, -1, -1))
    x.print("EEE")
    x.point_3d().print("DDD---")
    x.move_to_point_3d(Point_3D(-1, 1, 1))
    x.print("EEE")
    x.point_3d().print("DDD-++")
    x.move_to_point_3d(Point_3D(1, -1, 1))
    x.print("EEE")
    x.point_3d().print("DDD+-+")
    x.move_to_point_3d(Point_3D(1, 1, -1))
    x.print("EEE")
    x.point_3d().print("DDD++-")
    x.move_to_point_3d(Point_3D(1, -1, -1))
    x.print("EEE")
    x.point_3d().print("DDD+--")
    x.move_to_point_3d(Point_3D(-1, 1, -1))
    x.print("EEE")
    x.point_3d().print("DDD-+-")
    x.move_to_point_3d(Point_3D(-1, -1, 1))
    x.print("EEE")
    x.point_3d().print("DDD--+")

    print()
