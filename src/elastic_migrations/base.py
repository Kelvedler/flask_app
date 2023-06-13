import inspect
import os

DIRECTION_FORWARDS = 'forwards'
DIRECTION_REVERSE = 'reverse'
DIRECTIONS = (DIRECTION_FORWARDS, DIRECTION_REVERSE)


class MigrationError(Exception):
    pass


class Migration:

    def __init__(self, depends_on, forwards, reverse):
        self.filename = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0]
        self.depends_on = depends_on
        self.forwards = forwards
        self.reverse = reverse

    def run(self, direction):
        if direction == DIRECTION_FORWARDS:
            self.forwards()
        elif direction == DIRECTION_REVERSE:
            self.reverse()
        else:
            raise MigrationError('Unknown direction')
