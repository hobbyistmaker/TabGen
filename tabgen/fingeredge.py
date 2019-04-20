from collections import namedtuple


AxisChange = namedtuple('AxisChange', ['x', 'y', 'z'])


def distance(first, second):
    if (first.x == second.x) and (first.y == second.y):
        return first.z - second.z
    elif (first.y == second.y) and (first.z == second.z):
        return first.x - second.x
    elif (first.z == second.z) and (first.x == second.x):
        return first.y - second.y
    return 0


def changed_axis(vertices, second):
    xchanged, ychanged, zchanged = (0, 0, 0)

    for vertex in vertices:
        xchanged = 1 if (vertex.x != second.x) else 0
        ychanged = 1 if (vertex.y != second.y) else 0
        zchanged = 1 if (vertex.z != second.z) else 0

        if (xchanged + ychanged + zchanged) == 1:
            return vertex
    return second


class FingerEdge:

    def __init__(self, edge):
        self.__edge = edge

    @property
    def length(self):
        return self.__edge.length

    @property
    def end(self):
        return self.__edge.endVertex

    @property
    def start(self):
        return self.__edge.startVertex

    def distance(self, vertices, depth):
        start_point = self.start.geometry
        end_point = changed_axis(vertices, start_point)
        length = distance(start_point, end_point)

        return length - (depth if length > 0 else -depth)
