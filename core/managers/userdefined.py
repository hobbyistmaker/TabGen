import math

from .properties import Properties

def user_defined(inputs):
    finger_length = abs(inputs.width.value)
    face_length = abs(inputs.length.value)
    distance = abs(inputs.distance.value)
    depth = abs(inputs.depth.value)
    margin = abs(inputs.margin.value)

    adjusted_length = face_length - margin*2
    # We want to make sure that there are always at least 3 fingers on
    # a face, and that the number of fingers is always odd, since
    # there will be alternating tabs and notches
    fingers = (math.ceil(max(3, math.floor(adjusted_length / finger_length))/2)*2)-1

    finger_distance = finger_length * fingers

    if inputs.tab_first:
        pattern_distance = finger_distance - finger_length * 3
        # Start: where the finger drawing will start
        start = (face_length - finger_distance)/2 + finger_length
        # Offset: Portion of the face excluded from use
        offset = 0
        notches = math.floor(fingers/2)
    elif margin:
        # pattern_distance = finger_distance - finger_length * 5
        # offset = (face_length - finger_distance)/2 + finger_length
        # start = (face_length - finger_distance)/2 + finger_length*2
        pattern_distance = finger_distance - finger_length
        offset = (face_length - finger_distance)/2
        start = (face_length - finger_distance)/2
        notches = math.ceil(fingers/2)
    else:
        # If there isn't a margin, we'll offset the fingers from the
        # sides so that fingers on interior walls don't end up too close
        # to the edges.
        pattern_distance = finger_distance - finger_length * 5
        offset = (face_length - finger_distance)/2 + finger_length
        start = (face_length - finger_distance)/2 + finger_length*2
        notches = math.ceil(fingers/2) - 2

    return Properties(finger_length, face_length, distance, depth, margin,
                      adjusted_length, fingers, finger_length, start, notches,
                      pattern_distance, offset)


def user_defined_params(all_parameters, user_parameters,
                        finger_dimension, offset_dimension,
                        finger_cut, finger_pattern,
                        corner_cut, corner_pattern):
    pass
