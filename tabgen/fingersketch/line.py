from ..base import Base

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

        self._line = line
        self._start_point = line.startSketchPoint
        self._end_point = line.endSketchPoint
        self._start_geometry = self._start_point.geometry
        self._end_geometry = self._end_point.geometry

        self._line.isConstruction = construction

    @property
    def direction(self):
        spg = self._start_geometry
        epg = self._end_geometry
        return direction(spg, epg, self.is_vertical)

    @property
    def end(self):
        return self._end_point

    @property
    def first(self):
        return (self._start_point if self.direction
                else self._end_point)

    @property
    def first_geometry(self):
        return self.first.geometry

    @property
    def first_point(self):
        return self.first

    @property
    def is_vertical(self):
        return self._start_geometry.y != self._end_geometry.y

    @property
    def last(self):
        return (self._end_point if self.direction
                else self._start_point)

    @property
    def last_geometry(self):
        return self.last.geometry

    @property
    def last_point(self):
        return self.last

    @property
    def length(self):
        return self._line.length

    @property
    def sketch_line(self):
        return self._line

    @property
    def start(self):
        return self._start_point
