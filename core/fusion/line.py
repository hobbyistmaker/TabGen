import traceback

from collections import namedtuple

from adsk.fusion import BRepEdge
from adsk.fusion import SketchLine


Point = namedtuple('Point', ['point', 'vertex', 'geometry'])


def x_direction(start, end):
    return 1 if not x_reversed(start, end) else -1

def y_reversed(start, end):
    return not (start.y >= 0 and end.y >= 0 and end.y >= start.y)

def y_direction(start, end):
    return 1 if not y_reversed(start, end) else -1


def direction(point1, point2, vertical):
    if vertical:
        return y_direction(point1, point2)
    else:
        return x_direction(point1, point2)

def reversed(vertical, line):
    sg = line.startSketchPoint.geometry
    eg = line.endSketchPoint.geometry

    if vertical:
        return sg.y >= eg.y
    else:
        return sg.x >= eg.x


class Line:

    def __init__(self, line):
        self.line = line

        self.is_vertical = self.line.startSketchPoint.geometry.y != self.line.endSketchPoint.geometry.y
        self.length = self.line.length

        if self.line.isReference:
            self.edge = self.line.referencedEntity
            if self.edge.isParamReversed:
                self.end_vertex = getattr(self.edge, 'startVertex', None)
                self.start_vertex = getattr(self.edge, 'endVertex', None)
            else:
                self.start_vertex = getattr(self.edge, 'startVertex', None)
                self.end_vertex = getattr(self.edge, 'endVertex', None)
        else:
            self.edge = None
            self.start_vertex = None
            self.end_vertex = None

        self.start_point = self.line.startSketchPoint if self.reversed else self.line.endSketchPoint
        self.end_point = self.line.endSketchPoint if self.reversed else self.line.startSketchPoint

        self.end = Point(self.end_point,
                         self.end_vertex,
                         self.end_point.geometry)

        self.start = Point(self.start_point,
                           self.start_vertex,
                           self.start_point.geometry)

    @property
    def direction(self):
        spg = self.start_geometry
        epg = self.end_geometry
        return direction(spg, epg, self.is_vertical)

    @property
    def reversed(self):
        sg = self.line.startSketchPoint.geometry
        eg = self.line.endSketchPoint.geometry

        if self.is_vertical:
            return (eg.y >= sg.y)
        else:
            return (eg.x >= sg.x)


class Top(Line):

    @property
    def left(self):
        return self.start

    @property
    def right(self):
        return self.end


class Bottom(Line):

    @property
    def left(self):
        return self.start

    @property
    def right(self):
        return self.end


class Left(Bottom):
    pass


class Right(Top):
    pass
