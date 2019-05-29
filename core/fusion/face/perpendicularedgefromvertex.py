from collections import namedtuple


PerpendicularEdge = namedtuple('PerpendicularEdge', ['point', 'edge', 'other'])


class NoVertexError(Exception): pass


def perpendicular_edge_from_vertex(brepface, vertex):
    """ From a given vertex on the brepface, find the
        perpendicular edge on a connected brepface.
        """
    connected = vertex.edges

    if len(connected) == 0:
        raise NoVertexError

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


def edge_matches_points(edge, point1, point2):
    """ Find the face edge that matches the associated points.
        This can find the face edge that matches two points from
        a sketch line.
        """
    edge_start = edge.startVertex.geometry
    edge_end = edge.endVertex.geometry

    if ((edge_start.isEqualTo(point1) and edge_end.isEqualTo(point2)) or
       (edge_start.isEqualTo(point2) and edge_end.isEqualTo(point1))):
        return True
    return False

def edge_from_point(point, edge, reverse=False):
        """ Given a reference Point3D, return the vertex that
            matches.
            """
        if point.isEqualTo(edge.startVertex.geometry):
            return edge.endVertex if reverse else edge.startVertex
        if point.isEqualTo(edge.endVertex.geometry):
            return edge.startVertex if reverse else edge.endVertex

def perpendicular_edge_from_line(brepface, spoint, rpoint, ui):
    edges = brepface.edges

    ui.messageBox('perp_edge_from_line: {}'.format(len(edges)))
    for edge in edges:
        if edge_matches_point(edge, spoint, rpoint):
            continue

        connected = edge_from_point(spoint, edge)
        if not connected:
            continue

        for vedge in connected.edges:
            line = vedge.geometry
            if brepface.geometry.isPerpendicularToLine(line):
                return vedge
    else:
        return None
