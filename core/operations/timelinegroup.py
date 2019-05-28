from .operation import Operation


class TimelineGroup(Operation):

    def __init__(self, name, group):
        super().__init__()

        self.timeline = self.design.timeline if self.design else None
        self.name = name
        self.start = self.marker_position if self.timeline else 0

        self.operations = group()

        mp = self.marker_position
        lpos = mp if mp < self.count else self.count-1

        if self.timeline and self.is_valid and (lpos - self.start) > 1:
            group = self.groups.add(self.start, lpos)

    @property
    def count(self):
        if self.timeline:
            return self.timeline.count
        else:
            return 0

    @property
    def groups(self):
        return self.timeline.timelineGroups

    @property
    def is_valid(self):
        if self.timeline:
            return self.timeline.isValid
        else:
            return False

    @property
    def marker_position(self):
        if self.timeline:
            return self.timeline.markerPosition
        else:
            return 0
