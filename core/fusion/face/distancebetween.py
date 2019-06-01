from ..util import trim_zeros

from .vertexdistance import vertex_distance
from .vertexdistance import point_distance


def distance_between(brepface, brepedge):
    """ For the brepedge selected by the user, find the
        minimum distance between the brepedge and this
        brepface. This minimum distance will be used
        for the calculation that defines how far
        to cut the fingers on the secondary brepface.
        """
    if brepface.geometry.isParallelToLine(brepedge.geometry):
        this_vertices = [brepedge.startVertex,
                         brepedge.endVertex]

        return min(trim_zeros(vertex_distance(brepface.vertices,
                                              this_vertices)))
    else:
        return 0


def distance_between_faces(brepface, brepedge):
    """ For the brepedge selected by the user, find the
        minimum distance between the brepedge and this
        brepface. This minimum distance will be used
        for the calculation that defines how far
        to cut the fingers on the secondary brepface.
        """
    if brepface.geometry.isParallelToPlane(brepedge.geometry):
        primary_centroid = brepface.centroid
        second_centroid = brepedge.centroid

        return min(trim_zeros(point_distance([primary_centroid],
                                             [second_centroid])))
    else:
        return 0
