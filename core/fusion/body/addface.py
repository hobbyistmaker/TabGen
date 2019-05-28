from .faceid import next_face_id

def add_face(brepface):
    brepbody = brepface.body
    token = str(next_face_id(brepbody))

    face_id = brepface.attributes.itemByName('tabgen', 'face_id')
    if not face_id:
        face_id = brepface.attributes.add('tabgen', 'face_id', token)
    else:
        face_id.value = token

    bodytag = brepbody.attributes.itemByName('tabgen', 'tabbed_faces')
    bodytag.value = token

    return int(token)
