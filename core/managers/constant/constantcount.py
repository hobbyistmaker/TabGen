from collections import namedtuple
from math import ceil, floor

from adsk.core import ValueInput as vi

from ... import fusion

Property = namedtuple('Property', ['name', 'value', 'expression', 'comment'])


def create_constant_count(app, ui, inputs):
    return Fingers(app, ui, inputs)


class Fingers:

    def __init__(self, app, ui, inputs):
        self.app = app
        self.ui = ui

        self.parametric = not inputs.parametric
        self.tab_first = inputs.tab_first
        self.face = inputs.selected_face
        self.alternate = inputs.selected_edge

        self.name = inputs.name
        orientation = fusion.face_orientation(self.face)
        face_id = fusion.add_face(self.face)

        name = '{name} {orientation}{face_num}'.format(name=self.name,
                                                       orientation=orientation,
                                                       face_num=face_id)
        self.alias = fusion.clean_string(name)

        self.kerf = self._get_kerf(inputs.kerf)
        self.default_width = self._get_default_width(inputs.width)
        self.face_length = self._get_face_length(inputs.length)
        self.depth = self._get_depth(inputs.depth)
        self.distance = self._get_distance(inputs.distance)
        self.margin = self._get_margin(inputs.margin)
        self.interior = self._get_interior(inputs.interior)

        self.adjusted_length = self._get_adjusted_length(self._name, self.face_length, self.margin)
        self.fingers = self._get_fingers(self._name, self.adjusted_length, self.default_width)
        self.finger_length = self._get_finger_length(self._name, self.adjusted_length, self.fingers)
        self.finger_distance = self._get_finger_distance(self._name, self.finger_length, self.fingers, self.kerf)
        self.notches = self._get_notches(self._name, self.fingers, self.tab_first)
        self.pattern_distance = self._get_pattern_distance(self._name, self.adjusted_length, self.finger_length,
                                                           self.kerf, self.tab_first)
        self.distance_two = self._get_distance_two(self._name, self.distance, self.depth, self.kerf)
        self.start = self._get_start(self._name, self.margin, self.kerf, self.finger_length, self.tab_first)
        self.offset = self._get_offset(self._name, self.margin, self.kerf, self.tab_first)

    def _name(self, name):
        return '{}_{}'.format(self.alias, name)

    def _get_param(self, input_, name, comment, save=True):
        all_parameters = self.app.activeProduct.allParameters
        user_parameters = self.app.activeProduct.userParameters
        formula = 'abs({})'

        param = all_parameters.itemByName(getattr(input_, 'expression', ''))
        value = abs(input_.value)

        if param:
            expression = formula.format(param.name)
        else:
            if self.parametric and save:
                expression = user_parameters.add(self._name(name),
                                                 vi.createByString(formula.format(getattr(input_, 'expression',
                                                                                          input_.value))),
                                                 getattr(input_, 'unitType', ''),
                                                 'TabGen: {}'.format(comment)).name
            elif save:
                expression = formula.format(getattr(input_, 'expression', input_.value))
            else:
                expression = formula.format(getattr(input_, 'expression', self._name(name)))

        return Property(self._name(name), value, expression, comment)

    def _get_kerf(self, input_):
        return self._get_param(input_, 'kerf', 'kerf applied to offset cuts', save=False)

    def _get_interior(self, input_):
        return self._get_param(input_, 'interior_walls', 'number of interior walls', save=False)

    def _get_default_width(self, input_):
        return self._get_param(input_, 'default_width', 'default finger width', save=False)

    def _get_face_length(self, input_):
        return self._get_param(input_, 'face_length', 'length of the face to place fingers', save=False)

    def _get_distance(self, input_):
        return self._get_param(input_, 'distance', 'distance to secondary face', save=False)

    def _get_depth(self, input_):
        return self._get_param(input_, 'depth', 'depth of the notches to cut', save=False)

    def _get_margin(self, input_):
        return self._get_param(input_, 'margin', 'margin from the sides of the face to offset notches', save=False)

    @staticmethod
    def _get_adjusted_length(alias, face_length, margin):
        return Property(alias('adjusted_length'), face_length.value - margin.value * 2,
                        '(({}) - ({})*2)'.format(face_length.name, margin.name),
                        'adjusted length of the face without margins')

    @staticmethod
    def _get_fingers(alias, adjusted_length, default_width):
        return Property(alias('fingers'), (ceil(max(3, floor(adjusted_length.value / default_width.value))/2)*2)-1,
                        '((ceil(max(3; floor({} / {}))/2)*2)-1)'.format(adjusted_length.name,
                                                                        default_width.name),
                        'total number of fingers across the jointed faces')

    @staticmethod
    def _get_finger_length(alias, adjusted_length, fingers):
        return Property(alias('finger_length'), adjusted_length.value / fingers.value,
                        '({}/{})'.format(adjusted_length.name, fingers.name),
                        'nominal length of each finger')

    @staticmethod
    def _get_finger_distance(alias, finger_length, fingers, kerf):
        return Property(alias('finger_distance'), finger_length.value * fingers.value - kerf.value,
                        '(({}*{}/1mm) - {})'.format(finger_length.name, fingers.name, kerf.name),
                        'full distance of notch placement')

    @staticmethod
    def _get_notches(alias, fingers, tab_first):
        if tab_first:
            value = floor(fingers.value/2)
            expression = 'floor(({}/1mm)/2)'.format(fingers.name)
        else:
            value = ceil(fingers.value/2)
            expression = 'ceil(({}/1mm)/2)'.format(fingers.name)

        return Property(alias('notches'), value, expression, 'number of notches to cut in face')

    @staticmethod
    def _get_pattern_distance(alias, adjusted_length, finger_length, kerf, tab_first):
        if tab_first:
            value = adjusted_length.value - finger_length.value*3 + kerf.value/2
            expression = '(({} - {}*3) + {}/2)'.format(adjusted_length.name, finger_length.name, kerf.name)
        else:
            value = adjusted_length.value - finger_length.value + kerf.value/2
            expression = '(({} - {}) + {}/2)'.format(adjusted_length.name, finger_length.name, kerf.name)

        return Property(alias('pattern_distance'), value, expression,
                        'distance over which to place the rectangular pattern.')

    @staticmethod
    def _get_distance_two(alias, distance, depth, kerf):
        if distance.value:
            value = distance.value - depth.value + kerf.value/2
            expression = '({} + {} + {}/2)'.format(distance.name, depth.name, kerf.name)
        else:
            value = 0
            expression = '0'

        return Property(alias('second_distance'), value, expression, 'distance to second face.')

    @staticmethod
    def _get_start(alias, margin, kerf, finger_length, tab_first):
        if tab_first:
            value = margin.value + finger_length.value + kerf.value/2
            expression = '({} + {} + ({}/2))'.format(margin.name, finger_length.name, kerf.name)
        else:
            value = margin.value - kerf.value/2
            expression = '({} - ({}/2))'.format(margin.name, kerf.name)

        return Property(alias('start'), value, expression, 'start point for first notch')

    @staticmethod
    def _get_offset(alias, margin, kerf, tab_first):
        if tab_first:
            value = margin.value - kerf.value/2
            expression = '({} - ({}/2))'.format(margin.name, kerf.name)
        else:
            value = margin.value + kerf.value/2
            expression = '({} + ({}/2))'.format(margin.name, kerf.name)

        return Property(alias('offset'), value, expression, 'offset point for start of the finger distance')

    def save(self, properties):
        properties.adjusted.default_width.parameter.expression = self.default_width.expression
        properties.adjusted.face_length.parameter.expression = self.face_length.expression
        properties.adjusted.second_distance.parameter.expression = self.distance.expression
        properties.finger_dimension.parameter.expression = self.finger_length.expression
        properties.adjusted.fingers.parameter.expression = self.fingers.expression
        properties.offset_dimension.parameter.expression = self.start.expression
        properties.finger_cut.extentOne.distance.expression = '-{}'.format(self.depth.expression)

        left_dimension = getattr(properties, 'left_dimension', None)
        if left_dimension:
            properties.left_dimension.parameter.expression = self.offset.expression

        properties.marker.distance.parameter.expression = self.finger_distance.expression
        properties.adjusted.distance.parameter.expression = self.adjusted_length.expression
        properties.pattern.distance.parameter.expression = self.pattern_distance.expression
        properties.finger_pattern.distanceOne.expression = self.pattern_distance.name
        properties.finger_pattern.distanceTwo.expression = self.distance_two.expression
        properties.finger_pattern.quantityOne.expression = self.notches.expression
        properties.finger_pattern.quantityTwo.expression = '2 + {}'.format(self.interior.value)