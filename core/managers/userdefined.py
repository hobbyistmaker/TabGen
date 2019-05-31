import math

from adsk.core import ValueInput as vi

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
        # Offset: Portion of the face excluded from use
        offset = (face_length - finger_distance)/2
        # Start: where the finger drawing will start
        start = offset + finger_length
        notches = math.floor(fingers/2)
    else:
        pattern_distance = finger_distance - finger_length
        offset = (face_length - finger_distance)/2
        start = offset
        notches = math.ceil(fingers/2)

    return Properties(finger_length, face_length, distance, depth, margin,
                      adjusted_length, fingers, finger_length, start, notches,
                      pattern_distance, offset)


def user_defined_params(alias, all_parameters, user_parameters, inputs,
                     finger_dimension, start_dimension,
                     finger_cut, finger_pattern,
                     corner_cut, corner_pattern,
                     lcorner_dimension, rcorner_dimension):

    # finger_dimension.parameter.name = '{}_finger_width'.format(alias)
    # finger_pattern.quantityOne.name = '{}_notches'.format(alias)
    # finger_pattern.distanceOne.name = '{}_pattern_distance'.format(alias)
    # start_dimension.parameter.name = '{}_start_width'.format(alias)
    # finger_pattern.quantityTwo.name = '{}_walls'.format(alias)
    # finger_pattern.distanceTwo.name = '{}_secondary'.format(alias)
    # if lcorner_dimension:
        # lcorner_dimension.parameter.name = '{}_offset'.format(alias)

    wall_count = '({} + 2)'.format(inputs.interior.value)

    depth = set_parameter(alias, 'depth', inputs.depth,
                          all_parameters, finger_cut.extentOne.distance,
                          '-abs({})')

    face_param = all_parameters.itemByName(inputs.length.expression)
    if face_param:
        face_length = 'abs({})'.format(face_param.name)
    else:
        face_length = user_parameters.add('{}_length'.format(alias),
                                          vi.createByString('abs({})'.format(inputs.length.expression)),
                                          inputs.length.unitType,
                                          'TabGen: length of the face').name

    distance_param = all_parameters.itemByName(inputs.distance.expression)
    if distance_param:
        face_distance = 'abs({})'.format(distance_param.name)
    else:
        face_distance = user_parameters.add('{}_distance'.format(alias),
                                            vi.createByString('abs({})'.format(inputs.distance.expression)),
                                            inputs.distance.unitType,
                                            'TabGen: distance to secondary face').name

    margin_param = all_parameters.itemByName(inputs.margin.expression)
    if margin_param:
        margin = 'abs({})'.format(margin_param.name)
    else:
        margin = user_parameters.add('{}_margin'.format(alias),
                                     vi.createByString('abs({})'.format(inputs.margin.expression)),
                                     inputs.margin.unitType,
                                     'TabGen: margin from edge').name
    margin_truth = 'floor({0}/{0})'.format(margin)

    width_param = all_parameters.itemByName(inputs.width.expression)
    if width_param:
        finger_length = 'abs({})'.format(width_param.name)
    else:
        finger_length = user_parameters.add('{}_default_width'.format(alias),
                                            vi.createByString('abs({})'.format(inputs.width.expression)),
                                            inputs.width.unitType,
                                            'TabGen: default finger width').name

    adjusted_length = '(({}) - ({})*2)'.format(face_length, margin)
    fingers = '((ceil(max(3; floor({} / {}))/2)*2)-1)'.format(adjusted_length, finger_length)

    finger_dimension.parameter.expression = finger_length

    if inputs.tab_first:
        notches = 'floor({}/2)'.format(fingers)
        finger_count = '(({}*2/1pcs)+1)'.format(finger_pattern.quantityOne.name)
        finger_distance = '({} * {})'.format(finger_length, finger_count)
        pattern_distance = '({} - {}*3)'.format(finger_distance, finger_length)
    else:
        notches = 'ceil({}/2)'.format(fingers)
        finger_count = '(({}*2/1pcs)-1)'.format(finger_pattern.quantityOne.name)
        finger_distance = '({} * {})'.format(finger_length, finger_count)
        pattern_distance = '({} - {})'.format(finger_distance, finger_length)

    finger_pattern.quantityOne.expression = notches
    finger_pattern.distanceOne.expression = pattern_distance

    # start = '({} - {})/2 + {}'.format(face_length, finger_distance, finger_length)
    offset = '(({} - {})/2)'.format(face_length, finger_distance)

    # Corner dimensions cause a bug with adjacent faces -- no idea why
    if lcorner_dimension:
        lcorner_dimension.parameter.expression = offset
        start_fmt = '({})'.format(lcorner_dimension.parameter.name)
    else:
        start_fmt = offset

    if rcorner_dimension:
        rcorner_dimension.parameter.expression = lcorner_dimension.parameter.name

    if inputs.tab_first:
        start = '({} + {})'.format(start_fmt, finger_length)
    else:
        start = start_fmt

    start_dimension.parameter.expression = '{}'.format(start)

    finger_pattern.quantityTwo.expression = wall_count
    finger_pattern.distanceTwo.expression = '{} - abs({})'.format(face_distance, depth)

    if corner_cut:
        corner_cut.extentOne.distance.expression = finger_cut.extentOne.distance.name
    if corner_pattern:
        corner_pattern.quantityTwo.expression = '2'
        corner_pattern.distanceTwo.expression = finger_pattern.distanceTwo.name

def set_parameter(alias, name, input_, all_params, parameter, format_str):
    input_value = input_.expression

    param = all_params.itemByName(input_value)
    if param:
        expression = param.name
    else:
        expression = input_value

    parameter.expression = format_str.format(expression)
    # parameter.name = '{}_{}'.format(alias, name)
    return parameter.name
