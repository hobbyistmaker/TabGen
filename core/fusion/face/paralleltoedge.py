def parallel_to_edge(brepface, brepedge):
    if not brepface:
        return True

    return brepface.geometry.isParallelToLine(brepedge.geometry)

