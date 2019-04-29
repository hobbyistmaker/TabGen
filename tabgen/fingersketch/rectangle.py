import logging

from ...util import vertical
from .line import Line
from adsk.core import Application
app = Application.get()
ui = app.userInterface

logger = logging.getLogger('rectangle')


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
        logger.debug('Point ({}, {}, {}) = 1({}, {}, {}) or 1({}, {}, {})'.format(round(point.x, 3), round(point.y, 3), round(point.z, 3),
                                                                                  round(sp1.x, 3), round(sp1.y, 3), round(sp1.z, 3),
                                                                                  round(ep1.x, 3), round(ep1.y, 3), round(ep1.z, 3)))
        return first
    logger.debug('Point ({}, {}, {}) = 2({}, {}, {}) or 2({}, {}, {})'.format(round(point.x, 3), round(point.y, 3), round(point.z, 3),
                                                                              round(sp2.x, 3), round(sp2.y, 3), round(sp2.z, 3),
                                                                              round(ep2.x, 3), round(ep2.y, 3), round(ep2.z, 3)))
    return second


def bottom_line(axes):
    return compare_lines(axes[0], axes[1], lambda k: k.y, False)


def left_line(axes):
    return compare_lines(axes[0], axes[1], lambda k: k.x, False)


def right_line(axes):
    return compare_lines(axes[0], axes[1], lambda k: k.x, True)


def top_line(axes):
    return compare_lines(axes[0], axes[1], lambda k: k.y, True)


def debug_dump(rectangle):
    tlg = rectangle.top_left.geometry
    tlwg = rectangle.top_left.worldGeometry
    trg = rectangle.top_right.geometry
    trwg = rectangle.top_right.worldGeometry
    blg = rectangle.bottom_left.geometry
    blwg = rectangle.bottom_left.worldGeometry
    brg = rectangle.bottom_right.geometry
    brwg = rectangle.bottom_right.worldGeometry
    logger.debug('Rectangle Top Left: ({}, {}, {}) - ({}, {}, {})'.format(round(tlg.x*10, 3),
                                                                          round(tlg.y*10, 3),
                                                                          round(tlg.z*10, 3),
                                                                          round(tlwg.x*10, 3),
                                                                          round(tlwg.y*10, 3),
                                                                          round(tlwg.z*10, 3)))
    logger.debug('Rectangle Top Right: ({}, {}, {}) - ({}, {}, {})'.format(round(trg.x*10, 3),
                                                                           round(trg.y*10, 3),
                                                                           round(trg.z*10, 3),
                                                                           round(trwg.x*10, 3),
                                                                           round(trwg.y*10, 3),
                                                                           round(trwg.z*10, 3)))
    logger.debug('Rectangle Bottom Left: ({}, {}, {}) - ({}, {}, {})'.format(round(blg.x*10, 3),
                                                                             round(blg.y*10, 3),
                                                                             round(blg.z*10, 3),
                                                                             round(blwg.x*10, 3),
                                                                             round(blwg.y*10, 3),
                                                                             round(blwg.z*10, 3)))
    logger.debug('Rectangle Bottom Right: ({}, {}, {}) - ({}, {}, {})'.format(round(brg.x*10, 3),
                                                                              round(brg.y*10, 3),
                                                                              round(brg.z*10, 3),
                                                                              round(brwg.x*10, 3),
                                                                              round(brwg.y*10, 3),
                                                                              round(brwg.z*10, 3)))


class Rectangle:

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

    def __init__(self, sketch, lines):
        self.__lines = lines
        self.__sketch = sketch

        self.__set_width_length()
        self.__set_axes()

        debug_dump(self)

    def __set_axes(self):
        self.__vertical = vertical(self.__length_axes[0])

        if self.__vertical is True:
            tbaxes = self.__width_axes
            lraxes = self.__length_axes
        else:
            tbaxes = self.__length_axes
            lraxes = self.__width_axes

        self.__top = Line(top_line(tbaxes))
        self.__bottom = Line(bottom_line(tbaxes))
        self.__left = Line(left_line(lraxes))
        self.__right = Line(right_line(lraxes))

    def __set_width_length(self):
        lline1 = self.__lines.item(0)
        lline2 = self.__lines.item(1)

        self.__width = min(lline1.length, lline2.length)
        self.__length = max(lline1.length, lline2.length)

    @property
    def __length_axes(self):
        if self.__lines.item(0) == self.length:
            return (self.__lines.item(0),
                    self.__lines.item(2))
        return (self.__lines.item(1),
                self.__lines.item(3))

    @property
    def __width_axes(self):
        if self.__lines.item(0) == self.length:
            return (self.__lines.item(1),
                    self.__lines.item(3))
        return (self.__lines.item(0),
                self.__lines.item(2))

    @property
    def bottom(self):
        return self.__bottom

    @property
    def bottom_left(self):
        return self.bottom.first

    @property
    def bottom_right(self):
        return self.bottom.last

    @property
    def bottom_dir(self):
        return self.bottom.direction

    @property
    def left(self):
        return self.__left

    @property
    def left_bottom(self):
        return self.bottom_left

    @property
    def left_dir(self):
        return self.left.direction

    @property
    def left_top(self):
        return self.top_left

    @property
    def length(self):
        return self.__length

    @property
    def is_vertical(self):
        return self.left.length == self.__length

    @property
    def right(self):
        return self.__right

    @property
    def right_bottom(self):
        return self.bottom_right

    @property
    def right_top(self):
        return self.top_right

    @property
    def top(self):
        return self.__top

    @property
    def top_left(self):
        return self.top.last

    @property
    def top_right(self):
        return self.top.first

    @property
    def width(self):
        return self.__width
