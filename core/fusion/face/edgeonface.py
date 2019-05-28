def edge_on_face(brepface, brepedge):
    if not brepface or not brepedge:
        return False

    return brepedge in brepface.edges
