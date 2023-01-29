from math import fmod, cos, sin, sqrt, asin, acos
from random import random


#  dwh coordinates
#
#  h
#  ^
#  |    w
#  |   /|
#  |  /
#  | /
#  |/
# -+-----------> d
# /|
#

class Point_3D:
    def __init__(self, d, w, h):
        self.d = d  # distance aka X-horizontal, positive -  to right
        self.w = w  # width aka Y-isometric, positive - away
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


class Point_3D_Polar:
    pi = 3.14159

    def __init__(self, radius=0.0, azimuth=0.0, elevation=0.0):
        self.r = radius     # radius, keep always positive
        self.a = azimuth    # azimuth, rad, keep between 0..+360
        self.e = elevation  # elevation, rad (do not confuse with inclination), keep between -90..+90
        self.fix()

    def fix(self):
        if self.r < 0:                   # keep always positive
            self.r = -self.r
            self.a = self.a + 3.14159
            self.e = -self.e
        self.e = fmod(self.e, 2*3.14159)       # keep between -90..+90
        if self.e > 3.14159:
            self.a = self.a + 3.14159
            self.e = 3.14159 - self.e
        if self.e < -3.14159:
            self.a = self.a + 3.14159
            self.e = -3.14159 - self.e
        if self.e > 3.14159/2:
            self.a = self.a + 3.14159
            self.e = 3.14159 - self.e
        if self.e < -3.14159/2:
            self.a = self.a + 3.14159
            self.e = -3.14159 - self.e
        self.a = fmod(self.a, 2*3.14159)       # keep between 0..+360
        if self.a < 0:
            self.a += 2*3.14159

    def print(self, msg=None):
        if msg is None:
            print("3d point polar: r={0:.3f}, a={1:6.2f}° ({2:+6.4}), e={3:6.2f}° ({4:+6.4})".format(
                self.r, self.a*180/3.14159, self.a, self.e*180/3.14159, self.e
            ))
        else:
            print("{0}: r={1:.3f}, a={2:6.2f}° ({3:+6.4}), e={4:6.2f}° ({5:+6.4})".format(
                msg, self.r, self.a*180/3.14159, self.a, self.e*180/3.14159, self.e
            ))

    def move_to(self, r, a, e):
        self.r = r
        self.a = a
        self.e = e

    def add(self, x):
        return Point_3D_Polar(self.r+x.r, self.a+x.a, self.e+x.e)

    def sub(self, x):
        return Point_3D_Polar(self.a-x.a, self.a-x.a, self.e-x.e)

    def scale(self, x: float):
        return Point_3D_Polar(self.a*x, self.a, self.e)

    def random(self):
        return Point_3D_Polar(self.a*random(), 360*random(), 180*random()-90)

    def set_from_point_3d(self, x: Point_3D):
        r = sqrt(x.d*x.d+x.w*x.w+x.h*x.h)
        p = sqrt(x.d*x.d+x.w*x.w)
        sin_e = x.h/r
        cos_a = x.d/p
        self.r = r
        self.a = acos(cos_a)
        if x.w < 0:
            self.a = -self.a
        if self.a < 0:
            self.a = self.a + 2*3.14159
        self.e = asin(sin_e)
        return self

    def return_point_3d(self) -> Point_3D:
        d = self.r*cos(self.a)*cos(self.e)
        w = self.r*sin(self.a)*cos(self.e)
        h = self.r*sin(self.e)
        return Point_3D(d, w, h)
        pass


def rad(x):
    return 3.14159/180*x
    pass


def grad(x):
    return 180/3.14159*x
    pass


if __name__ == "__main__":

    center = Point_3D(250, 125, 125)
    center.print("AAA")
    print()

    center = Point_3D_Polar(250, rad(+10), rad(+10))
    center.print("BBB")
    center = Point_3D_Polar(250, rad(-10), rad(-10))
    center.print("BBB")
    center = Point_3D_Polar(250, rad(0), rad(+90+10))
    center.print("BBB")
    center = Point_3D_Polar(250, rad(0), rad(-90-10))
    center.print("BBB")
    center = Point_3D_Polar(250, rad(0), rad(+180+10))
    center.print("BBB")
    center = Point_3D_Polar(250, rad(0), rad(-180-10))
    center.print("BBB")
    print()

    center = Point_3D_Polar(1, rad(+45), rad(+45))
    center.return_point_3d().print("CCC")
    center = Point_3D_Polar(-1, rad(+180+45), rad(-45))
    center.return_point_3d().print("CCC")
    center = Point_3D_Polar(1, rad(+45), rad(-45))
    center.return_point_3d().print("CCC")
    center = Point_3D_Polar(1, rad(360-45), rad(+45))
    center.return_point_3d().print("CCC")
    print()

    x = Point_3D_Polar(0, 0, 0)
    x.set_from_point_3d(Point_3D(1, 1, 1))
    x.print("EEE")
    x.return_point_3d().print("DDD+++")
    x.set_from_point_3d(Point_3D(-1, -1, -1))
    x.print("EEE")
    x.return_point_3d().print("DDD---")
    x.set_from_point_3d(Point_3D(-1, 1, 1))
    x.print("EEE")
    x.return_point_3d().print("DDD-++")
    x.set_from_point_3d(Point_3D(1, -1, 1))
    x.print("EEE")
    x.return_point_3d().print("DDD+-+")
    x.set_from_point_3d(Point_3D(1, 1, -1))
    x.print("EEE")
    x.return_point_3d().print("DDD++-")
    x.set_from_point_3d(Point_3D(1, -1, -1))
    x.print("EEE")
    x.return_point_3d().print("DDD+--")
    x.set_from_point_3d(Point_3D(-1, 1, -1))
    x.print("EEE")
    x.return_point_3d().print("DDD-+-")
    x.set_from_point_3d(Point_3D(-1, -1, 1))
    x.print("EEE")
    x.return_point_3d().print("DDD--+")

    print()
