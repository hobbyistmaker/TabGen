from collections import namedtuple

from adsk.core import Point3D
from adsk.fusion import DimensionOrientations

from .util import vertical

from .line import Top, Bottom, Left, Right


ReferencePoint = namedtuple('ReferencePoint', ['first', 'second'])


def compare_lines(first, second, func, reverse):
    sp1 = first.startSketchPoint.geometry
    sp2 = second.startSketchPoint.geometry
    ep1 = first.endSketchPoint.geometry
    ep2 = second.endSketchPoint.geometry

    points = [sp1, sp2, ep1, ep2]
    point = sorted(points, key=func, reverse=reverse)[0]

    if point == sp1 or point == ep1:
        return first
    return second


def bottom_line(axes):
    return compare_lines(axes[0], axes[1], lambda k: k.y, False)


def left_line(axes):
    return compare_lines(axes[0], axes[1], lambda k: k.x, False)


def right_line(axes):
    return compare_lines(axes[0], axes[1], lambda k: k.x, True)


def top_line(axes):
    return compare_lines(axes[0], axes[1], lambda k: k.y, True)


class Rectangle:

    def __init__(self, lines):
        super().__init__()

        self.lines = lines

        self.__set_width_length(self.lines)
        self.__set_axes()

    def __set_axes(self):
        is_vertical = vertical(self.length_axes[0])

        if is_vertical is True:
            tbaxes = self.width_axes
            lraxes = self.length_axes
        else:
            tbaxes = self.length_axes
            lraxes = self.width_axes

        self.top = Top(top_line(tbaxes))
        self.bottom = Bottom(bottom_line(tbaxes))
        self.left = Left(left_line(lraxes))
        self.right = Right(right_line(lraxes))

    def __set_width_length(self, lines):
        lline1 = lines[0]
        lline2 = lines[1]

        self.width = min(lline1.length, lline2.length)
        self.length = max(lline1.length, lline2.length)

    @property
    def length_axes(self):
        if self.lines[0] == self.length:
            return (self.lines[0],
                    self.lines[2])
        return (self.lines[1],
                self.lines[3])

    @property
    def width_axes(self):
        if self.lines[0] == self.length:
            return (self.lines[1],
                    self.lines[3])
        return (self.lines[0],
                self.lines[2])

    @property
    def is_vertical(self):
        return self.left.length == self.length

    @property
    def reference_points(self):
        if self.is_vertical:
            return ReferencePoint(self.bottom.right.vertex,
                                  self.top.right.vertex)
        else:
            return ReferencePoint(self.bottom.left.vertex,
                                  self.bottom.right.vertex)

    @property
    def reference_line(self):
        return self.left.line if self.is_vertical else self.top.line

    def make_construction(self):
        for line in self.lines:
            line.isConstruction = True

    def offset_start(length):
        start = self.bottom.right.geometry if self.is_vertical else self.bottom.left.geometry
        return self.next_point(start, length, self.width)

    def next_point(start, length, width):
        if self.is_vertical:
            nextx = width
            nexty = length
        else:
            nextx = length
            nexty = width

        return Point3D.create(start.x + nextx, start.y + nexty, start.z)
