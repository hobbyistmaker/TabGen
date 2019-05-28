def check_if_edge(brepface):
    brepbody = brepface.body
    edges = sorted(brepbody.faces, key=lambda face: face.area)[:-2]
    return brepface in edges
