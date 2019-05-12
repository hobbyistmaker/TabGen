from ..core import Base
from ..util import distanceInputId
from ..util import dualEdgeSelectId
from ..util import fingerTypeId
from ..util import lengthInputId
from ..util import marginInputId
from ..util import mtlThickInputId
from ..util import parametricInputId
from ..util import selectedFaceInputId
from ..util import startWithTabInputId
from ..util import tabWidthInputId
from ..util import automaticWidthId


class TabConfig(Base):

    def __init__(self, inputs):
        super().__init__()

        self._inputs = inputs

    @property
    def default_width(self):
        if self._inputs:
            return self._inputs.itemById(tabWidthInputId)
        return None

    @property
    def depth(self):
        if self._inputs:
            return self._inputs.itemById(mtlThickInputId)
        return None

    @property
    def distance(self):
        if self._inputs:
            return self._inputs.itemById(distanceInputId)
        return None

    @property
    def edge(self):
        if self._inputs:
            entity = self._inputs.itemById(dualEdgeSelectId)
            if entity.selectionCount > 0:
                return entity.selection(0).entity
        return None

    @property
    def face(self):
        if self._inputs:
            entity = self._inputs.itemById(selectedFaceInputId)
            if entity.selectionCount > 0:
                return entity.selection(0).entity
        return None

    @property
    def finger_type(self):
        if self._inputs:
            input = self._inputs.itemById(fingerTypeId)
            if input:
                return input.selectedItem.name
        return automaticWidthId

    @property
    def length(self):
        if self._inputs:
            return self._inputs.itemById(lengthInputId)
        return None

    @property
    def margin(self):
        if self._inputs:
            return self._inputs.itemById(marginInputId)
        return None

    @property
    def parametric(self):
        if self._inputs:
            input = self._inputs.itemById(parametricInputId)
            if input:
                return input.value
        return False

    @property
    def start_with_tab(self):
        if self._inputs:
            input = self._inputs.itemById(startWithTabInputId)
            if input:
                return input.value
        return False
