import logging

from collections import namedtuple

from ...util import vertical

from ..base import Base

from .line import Top, Bottom, Left, Right


logger = logging.getLogger('rectangle')


ReferencePoint = namedtuple('ReferencePoint', ['first', 'second'])


def compare_lines(first, second, func, reverse):
    sp1 = first.startSketchPoint.geometry
    sp2 = second.startSketchPoint.geometry
    ep1 = first.endSketchPoint.geometry
    ep2 = second.endSketchPoint.geometry

    points = [sp1, sp2, ep1, ep2]
    point = sorted(points, key=func, reverse=reverse)[0]
    logger.debug('First Start: {}, {}, {}'.format(sp1.x, sp1.y, sp1.z))
    logger.debug('First End: {}, {}, {}'.format(ep1.x, ep1.y, ep1.z))
    logger.debug('Second Start: {}, {}, {}'.format(sp2.x, sp2.y, sp2.z))
    logger.debug('Second End: {}, {}, {}'.format(ep2.x, ep2.y, ep2.z))

    if point.isEqualTo(sp1) or point.isEqualTo(ep1):
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


class Rectangle(Base):

    @classmethod
    def draw(cls, sketch, first_point, second_point):
        lines = sketch.sketchCurves.sketchLines

        rectangle = Rectangle(sketch,
                              lines.addTwoPointRectangle(first_point,
                                                         second_point))

        sketch.geometricConstraints.addHorizontal(rectangle.bottom.sketch_line)
        sketch.geometricConstraints.addHorizontal(rectangle.top.sketch_line)
        sketch.geometricConstraints.addVertical(rectangle.left.sketch_line)
        sketch.geometricConstraints.addVertical(rectangle.right.sketch_line)

        return rectangle

    def __init__(self, sketch, lines, construction=False):
        super().__init__()

        self.lines = lines
        self.curves = sketch.sketchCurves
        self.sketch = sketch
        self.construction = construction

        self.__set_width_length()
        self.__set_axes()

    def __set_axes(self):
        construction = self.construction
        is_vertical = vertical(self.length_axes[0])

        if is_vertical is True:
            tbaxes = self.width_axes
            lraxes = self.length_axes
        else:
            tbaxes = self.length_axes
            lraxes = self.width_axes

        self.top = Top(top_line(tbaxes), construction)
        self.bottom = Bottom(bottom_line(tbaxes), construction)
        self.left = Left(left_line(lraxes), construction)
        self.right = Right(right_line(lraxes), construction)

    def __set_width_length(self):
        lline1 = self.lines[0]
        lline2 = self.lines[1]

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
            return ReferencePoint(self.top.right.vertex,
                                  self.top.left.vertex)

    @property
    def reference_line(self):
        return self.left.sketch_line if self.is_vertical else self.top.sketch_line
