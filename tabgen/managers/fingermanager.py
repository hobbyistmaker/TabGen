from adsk.core import Application
from adsk.core import ValueInput
from adsk.fusion import Design

from ...util import automaticWidthId
from ..fingerface import FingerFace
from ..fingersketch import FingerSketch
from ..parameters import FingerParameters

app = Application.get()
ui = app.userInterface

createByReal = ValueInput.createByReal
createByString = ValueInput.createByString


class FingerManager:

    finger_type = automaticWidthId

    @classmethod
    def create(cls, config):
        sc = [subclass for subclass in cls.__subclasses__()
              if subclass.finger_type == config.finger_type]
        return (sc[0](config)
                if len(sc) > 0
                else FingerManager(config))

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

        self.__config = FingerParameters.create(self, config)
        self.__face = FingerFace.create(self, self.__config)

    @property
    def config(self):
        return self.__config

    @property
    def face(self):
        return self.__face

    @property
    def sketch(self):
        return self.__sketch

    def execute(self):
        self.sketch = FingerSketch.create(self, self.face, self.config)

        if self.sketch.vertical:
            self.config.direction = self.face.y_direction
        else:
            self.config.direction = self.face.x_direction

        self.sketch.draw_fingers()
