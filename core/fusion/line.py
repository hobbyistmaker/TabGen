import traceback

from collections import namedtuple

from adsk.fusion import BRepEdge
from adsk.fusion import SketchLine

from ..base import Base


Point = namedtuple('Point', ['point', 'vertex', 'geometry'])


def x_direction(start, end):
    return 1 if (start.x >= 0
                 and end.x >= 0
                 and end.x >= start.x) else -1


def y_direction(start, end):
    return 1 if (start.y >= 0
                 and end.y >= 0
                 and end.y >= start.y) else -1


def direction(point1, point2, vertical):
    if vertical:
        return y_direction(point1, point2)
    else:
        return x_direction(point1, point2)


class Line(Base):

    def __init__(self, line, construction=False):
        super().__init__()
        self.line = line
        self.start_point = self.line.startSketchPoint
        self.end_point = self.line.endSketchPoint
        self.start_geometry = self.start_point.geometry
        self.end_geometry = self.end_point.geometry

        if self.line.isReference:
            self.referenced_entity = self.line.referencedEntity

        self.line.isConstruction = construction

    @property
    def direction(self):
        spg = self.start_geometry
        epg = self.end_geometry
        return direction(spg, epg, self.is_vertical)

    @property
    def end(self):
        return Point(self.end_point,
                     self.end_vertex,
                     self.end_point.geometry)

    @property
    def end_vertex(self):
        return self.referenced_entity.startVertex if self.reversed else self.referenced_entity.endVertex

    @property
    def is_vertical(self):
        return self.start_geometry.y != self.end_geometry.y

    @property
    def length(self):
        return self.line.length

    @property
    def reversed(self):
        if self.referenced_entity:
            return self.referenced_entity.isParamReversed
        else:
            return False

    @property
    def sketch_line(self):
        return self.line

    @property
    def start(self):
        return Point(self.start_point,
                     self.start_vertex,
                     self.start_point.geometry)

    @property
    def start_vertex(self):
        return self.referenced_entity.endVertex if self.reversed else self.referenced_entity.startVertex


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
        return self.end

    @property
    def right(self):
        return self.start


class Left(Bottom):
    pass


class Right(Top):
    pass
