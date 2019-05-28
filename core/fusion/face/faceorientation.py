from collections import namedtuple


Axis = namedtuple('Axis', ['name', 'value'])


def face_orientation(brepface):
    """ Make a basic attempt to determine the major axis orientation
        to make naming of created sketches and features somewhat
        useful.
        """
    uvector = brepface.geometry.uDirection.copy()
    vvector = brepface.geometry.vDirection.copy()

    uvector.normalize()
    vvector.normalize()

    combined = ((uvector.x + vvector.x)/2, (uvector.y + vvector.y)/2, (uvector.z + vvector.z)/2)

    axes = []
    if combined[0] != 0:
        axes.append(Axis('X', combined[0]))
    if combined[1] != 0:
        axes.append(Axis('Y', combined[1]))
    if combined[2] != 0:
        axes.append(Axis('Z', combined[2]))

    axes = sorted(axes, key=lambda key: key.value)
    count = len(axes)

    resultx = '{}'.format(axes[0].name) if count > 0 else ''
    resulty = resultx + '{}'.format(axes[1].name) if count > 1 else ''
    resultz = resulty + '{}'.format(axes[2].name) if count > 2 else ''

    return resultz
