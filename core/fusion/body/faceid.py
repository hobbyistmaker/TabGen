from .numberfaces import number_of_faces

def next_face_id(brepbody):
    return number_of_faces(brepbody) + 1
