from collections import namedtuple


PerpendicularEdge = namedtuple('PerpendicularEdge', ['point', 'edge', 'other'])


def perpendicular_edge_from_vertex(brepface, vertex):
    """ From a given vertex on the brepface, find the
        perpendicular edge on a connected brepface.
        """
    connected = vertex.edges

    other = connected[0].startVertex
    edge = None

    for testedge in connected:
        if brepface.geometry.isPerpendicularToLine(testedge.geometry):
            edge = testedge
            start = testedge.startVertex
            end = testedge.endVertex
            if start == vertex:
                other = end

    return PerpendicularEdge(vertex, edge, other)
