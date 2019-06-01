import math

from adsk.core import ValueInput as vi

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
    finger_distance = finger_length * fingers

    if inputs.tab_first:
        pattern_distance = adjusted_length - finger_length * 3
        start = margin + finger_length
        offset = margin
        notches = math.floor(fingers/2)
    else:
        pattern_distance = adjusted_length - finger_length
        offset = margin
        start = margin
        notches = math.ceil(fingers/2)

    return Properties(default_width, face_length, distance, depth, margin,
                      adjusted_length, fingers, finger_length, finger_distance, start, notches,
                      pattern_distance, offset)


def automatic_params(alias, all_parameters, user_parameters, inputs,
                     finger_dimension, offset_dimension,
                     finger_cut, finger_pattern,
                     finger_distance, adjusted_length,
                     pattern_distance,
                     corner_cut, corner_pattern,
                     lcorner_dimension, rcorner_dimension):

    wall_count = '({} + 2)'.format(inputs.interior.value)

    depth = set_parameter(inputs.depth,
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
        default_width = 'abs({})'.format(width_param.name)
    else:
        default_width = user_parameters.add('{}_default_width'.format(alias),
                                            vi.createByString('abs({})'.format(inputs.width.expression)),
                                            inputs.width.unitType,
                                            'TabGen: default finger width').name

    adjusted_length.parameter.expression = '(({}) - ({})*2)'.format(face_length, margin)
    fingers = '((ceil(max(3; floor({} / {}))/2)*2)-1)'.format(adjusted_length.parameter.name, default_width)
    finger_length = '({}/{})'.format(adjusted_length.parameter.name, fingers)

    finger_dimension.parameter.expression = finger_length
    finger_distance.parameter.expression = adjusted_length.parameter.name

    if inputs.tab_first:
        pattern_distance = '({} - {}*3)'.format(adjusted_length.parameter.name, finger_length)
        notches = 'floor({}/2)'.format(fingers)
    else:
        pattern_distance = '({} - {})'.format(adjusted_length.parameter.name, finger_length)
        notches = 'ceil({}/2)'.format(fingers, margin_truth)

    start = '({} + {})'.format(margin, finger_length)
    offset = '({})'.format(margin)

    offset_dimension.parameter.expression = start

    finger_pattern.quantityOne.expression = notches
    finger_pattern.distanceOne.expression = pattern_distance
    finger_pattern.quantityTwo.expression = wall_count
    finger_pattern.distanceTwo.expression = '{} - abs({})'.format(face_distance, depth)

    if lcorner_dimension:
        lcorner_dimension.parameter.expression = offset
    if rcorner_dimension:
        rcorner_dimension.parameter.expression = lcorner_dimension.parameter.name

    if corner_cut:
        corner_cut.extentOne.distance.expression = finger_cut.extentOne.distance.name
    if corner_pattern:
        corner_pattern.quantityTwo.expression = '2'
        corner_pattern.distanceTwo.expression = finger_pattern.distanceTwo.name


def set_parameter(input_, all_params, parameter, format_str):
    input_value = input_.expression

    param = all_params.itemByName(input_value)
    if param:
        expression = param.name
    else:
        expression = input_value

    parameter.expression = format_str.format(expression)
    return parameter.name
