from collections import namedtuple
from math import ceil, floor

from adsk.core import ValueInput as vi

from ... import fusion

Property = namedtuple('Property', ['name', 'value', 'expression', 'comment'])


def create_constant_width(app, ui, inputs):
    return ConstantWidthFingers(app, ui, inputs)


class ConstantWidthFingers:

    def __init__(self, app, ui, inputs):
        self.app = app
        self.ui = ui

        self.parametric = not inputs.parametric
        self.tab_first = inputs.tab_first
        self.face = inputs.selected_face
        self.alternate = inputs.selected_edge
        self.preview_enabled = inputs.preview
        self.units = self.app.activeProduct.unitsManager

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
        self.edge_margin = self._get_edge_margin(inputs.edge_margin)

        self.adjusted_length = self._get_adjusted_length(self._name, self.face_length, self.margin)
        self.adjusted_depth = self._get_adjusted_depth(self._name, self.depth, self.kerf)
        self.fingers = self._get_fingers(self._name, self.adjusted_length, self.default_width)
        self.finger_length = self._get_finger_length(self._name, self.default_width, self.kerf)
        self.adjusted_finger_length = self._get_adjusted_finger_length(self._name, self.finger_length, self.kerf)
        self.finger_distance = self._get_finger_distance(self._name, self.default_width, self.fingers, self.units)
        self.notches = self._get_notches(self._name, self.fingers, self.tab_first, self.units)
        self.pattern_distance = self._get_pattern_distance(self._name, self.finger_distance, self.default_width,
                                                           self.tab_first)
        self.distance_two = self._get_distance_two(self._name, self.distance, self.adjusted_depth,
                                                   self.edge_margin)
        self.offset = self._get_offset(self._name, self.face_length, self.finger_distance, self.kerf, self.tab_first)
        self.start = self._get_start(self._name, self.offset, self.default_width, self.kerf, self.tab_first)

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
        return self._get_param(input_, 'kerf',
                               'kerf applied to offset cuts',
                               save=False)

    def _get_interior(self, input_):
        return self._get_param(input_, 'interior_walls',
                               'number of interior walls',
                               save=False)

    def _get_default_width(self, input_):
        return self._get_param(input_, 'default_width',
                               'default finger width',
                               save=False)

    def _get_face_length(self, input_):
        return self._get_param(input_, 'face_length',
                               'length of the face to place fingers',
                               save=False)

    def _get_distance(self, input_):
        return self._get_param(input_, 'distance',
                               'distance to secondary face',
                               save=False)

    def _get_depth(self, input_):
        return self._get_param(input_, 'depth',
                               'depth of the notches to cut',
                               save=False)

    def _get_margin(self, input_):
        return self._get_param(input_, 'margin',
                               'margin from the sides of the face to offset notches',
                               save=False)

    def _get_edge_margin(self, input_):
        return self._get_param(input_, 'edge_margin',
                               'offset from face to cut notches',
                               save=False)

    @staticmethod
    def _get_adjusted_depth(alias, depth, kerf):
        return Property(alias('adjusted_depth'), abs(depth.value) - abs(kerf.value)/2,
                        '(abs({}) - abs({})/2)'.format(depth.name, kerf.name),
                        'kerf adjusted depth of notch')

    @staticmethod
    def _get_adjusted_length(alias, face_length, margin):
        return Property(alias('adjusted_length'), face_length.value - margin.value * 2,
                        '({}) - ({})*2'.format(face_length.name, margin.name),
                        'adjusted length of the face without margins')

    @staticmethod
    def _get_adjusted_finger_length(alias, finger_length, kerf):
        return Property(alias('adjusted_finger_length'), (abs(finger_length.value) - abs(kerf.value)),
                        '(abs({}) - abs({}))'.format(finger_length.name, kerf.name),
                        'kerf adjusted length of notches that are cut')

    @staticmethod
    def _get_fingers(alias, adjusted_length, default_width):
        return Property(alias('fingers'), (ceil(max(3, floor(adjusted_length.value / default_width.value))/2)*2)-1,
                        '((ceil(max(3; floor({} / {}))/2)*2)-1)'.format(adjusted_length.name,
                                                                        default_width.name),
                        'total number of fingers across the jointed faces')

    @staticmethod
    def _get_finger_length(alias, default_width, kerf):
        return Property(alias('finger_length'), default_width.value - kerf.value,
                        '({} - {})'.format(default_width.name, kerf.name),
                        'nominal length of each finger')

    @staticmethod
    def _get_finger_distance(alias, default_width, fingers, units):
        return Property(alias('finger_distance'), default_width.value * fingers.value,
                        '({}*{}/1{})'.format(default_width.name, fingers.name, units.defaultLengthUnits),
                        'full distance of notch placement')

    @staticmethod
    def _get_notches(alias, fingers, tab_first, units):
        if tab_first:
            value = floor(fingers.value/2)
            expression = 'floor(({}/1{})/2)'.format(fingers.name, units.defaultLengthUnits)
        else:
            value = ceil(fingers.value/2)
            expression = 'ceil(({}/1{})/2)'.format(fingers.name, units.defaultLengthUnits)

        return Property(alias('notches'), value, expression,
                        'number of notches to cut in face')

    @staticmethod
    def _get_pattern_distance(alias, finger_distance, default_width, tab_first):
        if tab_first:
            value = finger_distance.value - default_width.value*3
            expression = '(({} - {}*3))'.format(finger_distance.name, default_width.name)
        else:
            value = finger_distance.value - default_width.value
            expression = '({} - {})'.format(finger_distance.name, default_width.name)

        return Property(alias('pattern_distance'), value, expression,
                        'distance over which to place the rectangular pattern.')

    @staticmethod
    def _get_distance_two(alias, distance, depth, edge_margin):
        if distance.value:
            value = distance.value - depth.value - abs(edge_margin.value*2)
            expression = '({} - {} - abs({}*2))'.format(distance.name, depth.name, edge_margin.name)
        else:
            value = 0
            expression = '0'

        return Property(alias('second_distance'), value, expression,
                        'distance to second face.')

    @staticmethod
    def _get_start(alias, offset, finger_length, kerf, tab_first):
        if tab_first:
            value = offset.value + finger_length.value + kerf.value/2
            expression = '({} + {} + {})'.format(offset.name, finger_length.name, kerf.name)
        else:
            value = offset.value
            expression = '({})'.format(offset.name, kerf.name)

        return Property(alias('start'), value, expression,
                        'start point for first notch')

    @staticmethod
    def _get_offset(alias, face_length, finger_distance, kerf, tab_first):
        if tab_first:
            value = (face_length.value - finger_distance.value)/2 - kerf.value/2
            expression = '({} - {})/2 - {}/2'.format(face_length.name, finger_distance.name, kerf.name)
        else:
            value = (face_length.value - finger_distance.value)/2 + kerf.value/2
            expression = '({} - {})/2 + {}/2'.format(face_length.name, finger_distance.name, kerf.name)

        return Property(alias('offset'), value, expression,
                        'offset point for start of the finger distance')

    @property
    def ordered(self):
        return [
            self.default_width,
            self.margin,
            self.face_length,
            self.edge_margin,
            self.depth,
            self.kerf,
            self.distance,
            self.adjusted_depth,
            self.adjusted_length,
            self.fingers,
            self.finger_length,
            self.adjusted_finger_length,
            self.finger_distance,
            self.pattern_distance,
            self.distance_two,
            self.offset,
            self.start
        ]

    def save(self, properties):
        properties.sketch.isComputeDeferred = True
        # properties.default_width.parameter.expression = self.default_width.expression
        # properties.face_length.parameter.expression = self.face_length.expression
        # properties.edge_margin.parameter.expression = self.edge_margin.expression
        # properties.second_distance.parameter.expression = self.distance_two.expression
        # properties.finger_dimension.parameter.expression = self.adjusted_finger_length.expression
        # properties.adjusted_finger_length.parameter.expression = self.adjusted_finger_length.expression
        # properties.finger_count.parameter.expression = self.fingers.expression
        # properties.adjusted_length.parameter.expression = self.adjusted_length.expression
        # properties.adjusted_depth.parameter.expression = self.adjusted_depth.expression
        properties.finger_cut.extentOne.distance.expression = '-{}'.format(self.adjusted_depth.name)

        # properties.start_dimension.parameter.expression = self.start.expression
        # properties.finger_distance.parameter.expression = self.finger_distance.expression
        # properties.pattern_distance.parameter.expression = self.pattern_distance.expression
        properties.finger_pattern.distanceOne.expression = self.pattern_distance.name
        properties.finger_pattern.distanceTwo.expression = self.distance_two.name
        properties.finger_pattern.quantityOne.expression = self.notches.expression
        properties.finger_pattern.quantityTwo.expression = '2 + {}'.format(self.interior.value)
        # properties.offset_dimension.parameter.expression = self.offset.expression

        left_dimension = getattr(properties, 'left_dimension', None)
        if left_dimension:
            properties.left_dimension.parameter.expression = self.offset.name
        right_dimension = getattr(properties, 'right_dimension', None)
        if right_dimension:
            properties.left_dimension.parameter.expression = self.offset.name
        properties.sketch.isComputeDeferred = False
