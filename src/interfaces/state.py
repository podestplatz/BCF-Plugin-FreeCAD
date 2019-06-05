from enum import Enum

class State:
    class States(Enum):
        ORIGINAL = 1
        ADDED = 2
        DELETED = 3
        MODIFIED = 4

    def __init__(self, state=States.ORIGINAL):
        self.state = state

