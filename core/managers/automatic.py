import math

from .properties import Properties

def automatic(inputs):
    default_width = abs(inputs.width.value)
    face_length = abs(inputs.length.value)
    distance = abs(inputs.distance.value)
    depth = abs(inputs.depth.value)
    margin = abs(inputs.margin.value)

    adjusted_length = face_length - margin*2
    fingers = (math.ceil(max(3, math.floor(adjusted_length / default_width))/2)*2)-1

    finger_length = adjusted_length / fingers

    if inputs.tab_first:
        pattern_distance = adjusted_length - finger_length * 3
        start = offset = finger_length + margin
        notches = math.floor(fingers/2)
    elif margin:
        pattern_distance = adjusted_length - finger_length * 3
        offset = finger_length + margin
        start = finger_length * 2 + margin
        notches = math.ceil(fingers/2) - 2
    else:
        pattern_distance = adjusted_length - finger_length
        offset = start = 0
        notches = math.ceil(fingers/2)

    return Properties(default_width, face_length, distance, depth, margin,
                      adjusted_length, fingers, finger_length, start, notches,
                      pattern_distance, offset)


def automatic_params(all_parameters, user_parameters,
                     finger_dimension, offset_dimension,
                     finger_cut, finger_pattern,
                     corner_cut, corner_pattern):
    pass
