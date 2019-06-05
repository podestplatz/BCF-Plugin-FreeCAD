from interfaces.hierarchy import Hierarchy
from interfaces.state import State

"""
Wrapper class for a URI, maybe will get replaced by the uri module in the
future
"""
class Uri(Hierarchy, State):
    def __init__(self,
            uri: str,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        self.uri = uri


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return self.uri == other.uri

    def __str__(self):
        ret_str = "Uri({})".format(self.uri)
        return ret_str
