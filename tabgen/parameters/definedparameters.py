import math

from ...util import userDefinedWidthId
from .fingerparameters import FingerParameters
from .fingerparameter import FingerParameter
from adsk.core import Application

app = Application.get()
ui = app.userInterface

class DefinedParameters(FingerParameters):

    finger_type = userDefinedWidthId

    def __init__(self, parent, config, directions):
        super().__init__(parent, config, directions)

        if self.parametric:
            width = self.width.name
            length = self.length.name
            margin = self.margin.name
            distance = self.distance.name
            depth = self.depth.name
        else:
            width = self.width.expression
            length = self.length.expression
            margin = self.margin.expression
            distance = self.distance.expression
            depth = self.depth.expression

        self.adjusted_length = FingerParameter(self._name('adjusted_length'),
                                                '({0} - abs({1})*2)'.format(length, margin),
                                                self.config.length.value - (abs(self.config.margin.value)*2),
                                                'Adjusted length, including margin')
        self.estimated_fingers = FingerParameter(self._name('estimated_fingers'),
                                                  'floor({0} / {1})'.format(self.adjusted_length.expression,
                                                                                 width),
                                                  math.floor(self.adjusted_length.value / self.config.default_width.value),
                                                  'Estimated number of fingers',
                                                  units='')
        self.fingers = FingerParameter(self._name('fingers'),
                                        'max(3, ({0} * 2) - 1)'.format(self.estimated_fingers.expression),
                                        max(3, (self.estimated_fingers.value * 2) - 1),
                                        'Actual number of fingers along the face',
                                        units='')

        if self.config.start_with_tab:
            self.tabs = FingerParameter(self._name('tabs'),
                                             'ceil({0} / 2)'.format(self.estimated_fingers.expression),
                                             math.ceil(self.estimated_fingers.value / 2),
                                             'Number of tabs to leave',
                                             units='')
            self.notches = FingerParameter(self._name('notches'),
                                               '{0} - 1'.format(self.tabs.expression),
                                               self.tabs.value - 1,
                                               'Number of notches to cut',
                                               units='')
            self.cut_distance = FingerParameter(self._name('cut_distance'),
                                                '{0} * {1} - {0}*2'.format(width,
                                                                           self.fingers.expression),
                                                self.config.default_width.value * self.fingers.value - (self.config.default_width.value*2),
                                                'Distance over which to place the cut notches')
        else:
            self.notches = FingerParameter(self._name('notches'),
                                               'ceil({0} / 2)'.format(self.estimated_fingers.expression),
                                               math.ceil(self.estimated_fingers.value / 2),
                                               'Number of notches to cut',
                                               units='')
            self.tabs = FingerParameter(self._name('tab_count'),
                                             '{0} - 1'.format(self.tabs.expression),
                                             self.tabs.value - 1,
                                             'Number of tabs to leave',
                                             units='')
            self.cut_distance = FingerParameter(self._name('cut_distance'),
                                                '{0} * {1} - {0}*2'.format(width,
                                                                           self.fingers.expression),
                                                self.config.default_width.value * self.fingers.value - (self.config.default_width.value*2),
                                                'Distance over which to place the cut notches')

        self.offset = FingerParameter(self._name('offset'),
                                      'abs({} - {} - {})/2'.format(length,
                                                                 self.cut_distance.name,
                                                                 width),
                                      abs((self.length.value - self.cut_distance.value - self.default_width.value)/2)/10,
                                      units='mm')

        self.leftcorner = FingerParameter(self._name('lcwidth'),
                                          'abs({} + {})'.format(self.offset.name, self.margin.name),
                                          abs(self.offset.value + self.margin.value),
                                          units='mm')
        ui.messageBox('Offset value: {}'.format(self.offset.value))

        self.notch_length = FingerParameter(self._name('notch_length'),
                                            '{0} * (({1}-2)*2)'.format(width, self.notches.name),
                                            self.default_width.value * ((self.notches.value-2)*2))

    def save_all(self):
        self.length.save(favorite=True)
        self.width.save(favorite=True)
        self.margin.save(favorite=True)
        # self.offset.save()

        if self.distance.value > 0:
            self.distance.save()

    # @property
    # def adjusted_length(self):
    #     return self._adjusted_length

    # @property
    # def estimated_fingers(self):
    #     return self._estimated_fingers

    # @property
    # def estimated_tabs(self):
    #     return self._estimated_tabs

    # @property
    # def finger_count(self):
    #     return self._fingers

    # @property
    # def tab_count(self):
    #     if self.config.start_with_tab:
    #         return math.ceil(self.finger_count / 2)
    #     else:
    #         return self.notch_count - 1

    # @property
    # def notch_count(self):
    #     if self.config.start_with_tab:
    #         return self.tab_count - 1
    #     else:
    #         return math.ceil(self.finger_count / 2) - 2

    # @property
    # def offset(self):
    #     return self._offset

    # @property
    # def notch_length(self):
    #     return self._notch_length

        # length = self.length - abs(tc.margin.value)*2
        # default_finger_count = max(3,
        #                        (math.ceil(math.floor(length / tc.default_width.value)/2)*2)-1)
        # if tc.start_with_tab:
        #     default_tab_count = math.ceil(default_finger_count/2)
        #     default_notch_count = default_tab_count - 1
        #     tab_length = tc.default_width.value * default_finger_count - tc.default_width.value*2
        # else:
        #     default_notch_count = math.ceil(default_finger_count/2) - 2
        #     default_tab_count = default_notch_count - 1
        #     tab_length = tc.default_width.value * default_finger_count

        # tab_length = tc.default_width.value * default_finger_count + tc.default_width.value
        # margin = (self.length - tab_length + tc.default_width.value) / 2
        # default_width = tc.default_width.value

        # if tc.start_with_tab is True:
        #     distance = length - margin*2 - default_width
        #     extrude_count = default_tab_count
        # else:
        #     distance = length - margin*2 - default_width*3
        #     extrude_count = default_tab_count - 1

        # tab_width = tc.default_width.value


