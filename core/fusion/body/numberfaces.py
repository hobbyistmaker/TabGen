def number_of_faces(brepbody):
    token = brepbody.attributes.itemByName('tabgen', 'tabbed_faces')
    if not token:
        token = brepbody.attributes.add('tabgen', 'tabbed_faces', str(0))

    return int(token.value)
