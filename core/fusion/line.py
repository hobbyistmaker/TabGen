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

        self.is_vertical = (round(self.line.startSketchPoint.geometry.x, 5) ==
                            round(self.line.endSketchPoint.geometry.x, 5))
        self.length = self.line.length

        if self.line.isReference:
            self.edge = self.line.referencedEntity
        else:
            self.edge = None

        if self.edge:
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

        self.start_point = self.line.startSketchPoint if not self.reversed else self.line.endSketchPoint
        self.end_point = self.line.endSketchPoint if not self.reversed else self.line.startSketchPoint

        self.end = Point(self.end_point,
                         self.end_vertex,
                         self.end_point.geometry)

        self.start = Point(self.start_point,
                           self.start_vertex,
                           self.start_point.geometry)

    def find_reference(self, line, face):
        line_start = line.startSketchPoint.worldGeometry
        line_end = line.endSketchPoint.worldGeometry

        for edge in face.edges:
            start = edge.startVertex
            end = edge.endVertex
            if ((line_start.isEqualTo(start) and line_end.isEqualTo(end)) or
                (line_end.isEqualTo(start) and line_start.isEqualTo(end))):
                return edge

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
            return (eg.y <= sg.y)
        else:
            return (0 < sg.x > eg.x) or (0 > eg.x < sg.x < 0)


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
