from collections import namedtuple

Dimensions = namedtuple('Dimensions', ['width', 'length'])

def dimensions(brepface):
    if not brepface:
        return 0

    evaluator = brepface.evaluator
    prange = evaluator.parametricRange()

    x_length = prange.maxPoint.x - prange.minPoint.x
    y_length = prange.maxPoint.y - prange.minPoint.y

    width = min(x_length, y_length)
    length = max(x_length, y_length)

    return Dimensions(width, length)
