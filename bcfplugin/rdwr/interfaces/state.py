from enum import Enum

class State:
    class States(Enum):
        ORIGINAL = 1
        ADDED = 2
        DELETED = 3
        MODIFIED = 4

    def __init__(self, state=States.ORIGINAL):
        self.state = state


    def isOriginal(self)-> 'bool':
        return self.state == State.States.ORIGINAL


    def getStateList(self)-> 'List[Tuple[State, Object]]':

        """
        Every class implementing this function shall compile a list of tuples
        one list element for each member object. Each list element has as first
        tuple element the state of the object
        (state.State.States.[ADDED|DELETED|MODIFIED|ORIGINAL]) and as second
        element the object itself.
        """
        stateList = list()
        if not self.isOriginal():
            stateList.append((self.state, self))

        return stateList

