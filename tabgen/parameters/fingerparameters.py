from adsk.core import Application
from adsk.fusion import Design
from adsk.core import ValueInput

from ...util import automaticWidthId
from .fingerparameter import FingerParameter

app = Application.get()
ui = app.userInterface


class FingerParameters:

    finger_type = automaticWidthId

    @classmethod
    def create(cls, config):
        sc = [subclass for subclass in cls.__subclasses__()
              if subclass.finger_type == config.finger_type]
        return (sc[0](config)
                if len(sc) > 0
                else FingerParameters(config))

    def __init__(self, config):
        self._des = Design.cast(app.activeProduct)
        self._user_params = self._des.userParameters

        self.__manager = manager
        self.__config = config
        self.__directions = None

        face_count = config.face.body.attributes.itemByName('tabgen', 'faces')
        self.__face_num = (face_count + 1) if face_count else 1
        self.__faces = [config.face.body.faces.item(j)
                        for j in range(0, config.face.body.faces.count)]
        self.__edges = [config.face.body.edges.item(j)
                        for j in range(0, config.face.body.edges.count)]
        self.__edge_faces = sorted(self.__faces, key=lambda face: face.area)[:-2]
        self.__name = self.body.name

        self.__timeline = self._des.timeline

        evaluator = self.face.geometry.evaluator
        pRange = evaluator.parametricRange()
        self.__xlen = pRange.maxPoint.x - pRange.minPoint.x
        self.__ylen = pRange.maxPoint.y - pRange.minPoint.y

        self.parameters = []

        self.__create_default_parameters(config)

    def __clean_name(self, param):
        for ch in [' ', '-', '(', ')']:
            if ch in param:
                param = param.replace(ch, '_')
        return param.lower()

    def _set_prefix(self):
        prefix = self.config.face.body.name

        if self.directions:
            dirname = directions[1] if parent.vertical else directions[0]
        else:
            dirname = ''

        self._clean_name = self.__clean_name(prefix)
        self.prefix = '{name}_{dirname}{facenum}'.format(self._clean_name,
                                                         dirname,
                                                         self.__face_num)

    def _name(self, value):
        return '{prefix}_{name}'.format(prefix=self.prefix, name=value)

    def __create_default_parameters(self, config):
        self._set_prefix()

        save = self.config.parametric

        if self.parametric:
            length = self.config.length.name
        else:
            length = self.config.length.expression

        margin = self.config.margin.expression
        marginval = self.config.margin.value
        lengthval = self.config.length.value

        self.margin = FingerParameter('margin',
                                      config.margin.expression,
                                      config.margin.value,
                                      'Auto: minimum margin from edge',
                                      'cm')
        self.width = FingerParameter('width',
                                     config.default_width.expression,
                                     config.default_width.value,
                                     'Auto: target finger width',
                                     'cm')
        self.length = FingerParameter('length',
                                      config.length.expression,
                                      config.length.value,
                                      'Auto: length of the face',
                                      'cm',
                                      save=save)
        self.distance = FingerParameter('distance',
                                        config.distance.expression,
                                        config.distance.value,
                                        'Auto: distance to second edge',
                                        'cm')
        self.depth = FingerParameter('depth',
                                     config.depth.expression,
                                     config.depth.value,
                                     'Auto: depth to cut the fingers',
                                     'cm')
        self.adjusted_length = FingerParameter('adjusted_length',
                                               '({length} - abs({margin})*2)'.format(length=length,
                                                                                     margin=margin),
                                               lengthval - (abs(marginval)*2),
                                               'Auto: Adjusted length, including margin')

    @property
    def config(self):
        return self.__config

    @property
    def body(self):
        return self.face.body

    @property
    def default_width(self):
        return self.config.default_width

    @property
    def directions(self):
        return self.__directions

    @directions.setter
    def directions(self, value):
        self.__directions = value
        self._set_prefix()

    @property
    def edge_selected(self):
        if self.face:
            return self.face in self.faces
        return False

    @property
    def face(self):
        return self.config.face

    @property
    def faces(self):
        return self.__faces

    @property
    def face_id(self):
        return self.__face_num

    @property
    def features(self):
        return self.parent.features

    @property
    def parent(self):
        return self.body.parentComponent

    @property
    def parametric(self):
        return self.config.parametric

    @property
    def rectangular_patterns(self):
        return self.features.rectangularPatternFeatures

    @property
    def manager(self):
        return self.__manager

    @property
    def start_with_tab(self):
        return self.config.start_with_tab

    @property
    def vertical(self):
        return self.config.vertical

    @property
    def x_length(self):
        return self.__xlen

    @property
    def y_length(self):
        return self.__ylen
