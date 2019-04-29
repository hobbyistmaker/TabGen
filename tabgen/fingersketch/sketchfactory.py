from ...util import automaticWidthId, userDefinedWidthId

from .autosketch import AutoSketch
from .definedsketch import DefinedSketch


def sketch_factory(face, params, ui=None):
    if params.finger_type == automaticWidthId:
        return AutoSketch(face, params, ui)
    elif params.finger_type == userDefinedWidthId:
        return DefinedSketch(face, params, ui)
