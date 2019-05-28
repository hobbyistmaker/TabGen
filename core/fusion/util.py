import math

class DistanceCalculationException(Exception): pass


def clean_string(param):
    for ch in [' ', '-', '(', ')']:
        if ch in param:
            param = param.replace(ch, '_')
    return param.lower()

def vertical(line):
    start = line.startSketchPoint.geometry
    end = line.endSketchPoint.geometry
    return start.y != end.y

def distance(a, b):
    try:
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)
    except:
        raise DistanceCalculationException

def trim_zeros(list_):
    return [val for val in list_ if val != 0]
