import math

from adsk.core import ValueInput as vi

from .properties import Properties

def automatic(inputs):
    default_width = abs(inputs.width.value)
    face_length = abs(inputs.length.value)
    distance = abs(inputs.distance.value)
    depth = abs(inputs.depth.value)
    margin = abs(inputs.margin.value)

    adjusted_length = (face_length/repeats) - margin*2
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


def automatic_params(alias, all_parameters, user_parameters, inputs,
                     finger_dimension, offset_dimension,
                     finger_cut, finger_pattern,
                     corner_cut, corner_pattern,
                     lcorner_dimension, rcorner_dimension):

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
        default_width = 'abs({})'.format(width_param.name)
    else:
        default_width = user_parameters.add('{}_default_width'.format(alias),
                                            vi.createByString('abs({})'.format(inputs.width.expression)),
                                            inputs.width.unitType,
                                            'TabGen: default finger width').name

    adjusted_length = '({}) - ({})*2'.format(face_length, margin)
    fingers = '(ceil(max(3; floor(({}) / ({})))/2)*2)-1'.format(adjusted_length, default_width)
    finger_length = '({}) / ({})'.format(adjusted_length, fingers)

    finger_dimension.parameter.expression = finger_length
    finger_dimension.parameter.name = '{}_finger_width'.format(alias)

    if inputs.tab_first:
        pattern_distance = '({}) - ({}) * 3'.format(adjusted_length, finger_length)
        start = offset = '({}) + ({})'.format(finger_dimension.parameter.name, margin)
        notches = 'floor(({})/2)'.format(fingers)
    else:
        pattern_distance = '({}) - ({}) * (3*{})'.format(adjusted_length, finger_length, margin_truth)
        offset = '(({}) + ({}))*{}'.format(finger_dimension.parameter.name, margin, margin_truth)
        start = '(({})*2 + ({}))*{}'.format(finger_dimension.parameter.name, margin, margin_truth)
        notches = 'ceil(({})/2) - (2*{})'.format(fingers, margin_truth)

    offset_dimension.parameter.expression = offset
    offset_dimension.parameter.name = '{}_offset_width'.format(alias)

    finger_pattern.quantityOne.expression = notches
    finger_pattern.quantityOne.name = '{}_notches'.format(alias)
    finger_pattern.distanceOne.expression = pattern_distance
    finger_pattern.distanceOne.name = '{}_pattern_distance'.format(alias)
    finger_pattern.quantityTwo.expression = wall_count
    finger_pattern.quantityTwo.name = '{}_walls'.format(alias)
    finger_pattern.distanceTwo.expression = '{} - abs({})'.format(face_distance, depth)
    finger_pattern.distanceTwo.name = '{}_secondary'.format(alias)

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
    parameter.name = '{}_{}'.format(alias, name)
    return parameter.name
