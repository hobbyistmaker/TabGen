import traceback

from collections import namedtuple

from adsk.fusion import BRepEdge
from adsk.fusion import SketchLine

from ..base import Base


Point = namedtuple('Point', ['point', 'vertex', 'geometry'])


def x_direction(start, end):
    return True if (start.x >= 0
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

        start = self.line.startSketchPoint.geometry
        end = self.line.endSketchPoint.geometry

        self.is_vertical = start.y != end.y
        self.length = self.line.length
        self.sketch_line = self.line

        self.parent_reversed = direction(start, end, self.is_vertical)

        if self.line.isReference:
            self.referenced_entity = self.line.referencedEntity
            self.start_vertex = getattr(self.referenced_entity, 'startVertex', None)
            self.end_vertex = getattr(self.referenced_entity, 'endVertex', None)
        else:
            self.referenced_entity = None

            # self.parent_reversed = False
            self.start_vertex = None
            self.end_vertex = None

        if getattr(self, 'parent_reversed', False):
            self.start_point = self.line.endSketchPoint
            self.end_point = self.line.startSketchPoint
            self.start_geometry = end
            self.end_geometry = start
        else:
            self.start_point = self.line.startSketchPoint
            self.end_point = self.line.endSketchPoint
            self.start_geometry = start
            self.end_geometry = end

        self.end = Point(self.end_point,
                         self.end_vertex,
                         self.end_point.geometry)

        self.start = Point(self.start_point,
                           self.start_vertex,
                           self.start_point.geometry)

        self.line.isConstruction = construction

    @property
    def direction(self):
        spg = self.start_geometry
        epg = self.end_geometry
        return direction(spg, epg, self.is_vertical)


class Top(Line):

    @property
    def left(self):
        return self.end

    @property
    def right(self):
        return self.start


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
