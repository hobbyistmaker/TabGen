def distance_between(app, brepface, brepedge):
    """ For the brepedge selected by the user, find the
        minimum distance between the brepedge and this
        brepface. This minimum distance will be used
        for the calculation that defines how far
        to cut the fingers on the secondary brepface.
        """
    if brepface.geometry.isParallelToLine(brepedge.geometry):
        return app.measureManager.measureMinimumDistance(brepface.geometry, brepedge.geometry).value
    else:
        return 0


def distance_between_faces(app, brepface, brepedge):
    """ For the brepedge selected by the user, find the
        minimum distance between the brepedge and this
        brepface. This minimum distance will be used
        for the calculation that defines how far
        to cut the fingers on the secondary brepface.
        """
    if brepface.geometry.isParallelToPlane(brepedge.geometry):
        return app.measureManager.measureMinimumDistance(brepface.geometry, brepedge.geometry).value
    else:
        return 0
