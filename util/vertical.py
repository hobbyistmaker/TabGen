def vertical(line):
    start = line.startSketchPoint.geometry
    end = line.endSketchPoint.geometry
    return start.y != end.y
