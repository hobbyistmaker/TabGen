from adsk.core import Point3D


def next_point(start, length, width, vertical):
    if vertical:
        nextx = width
        nexty = length
    else:
        nextx = length
        nexty = width

    return Point3D.create(start.x + nextx, start.y + nexty, start.z)
