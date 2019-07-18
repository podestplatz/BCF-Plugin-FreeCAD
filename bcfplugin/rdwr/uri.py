from copy import deepcopy
from rdwr.interfaces.hierarchy import Hierarchy
from rdwr.interfaces.state import State
from rdwr.interfaces.identifiable import Identifiable

class Uri(Hierarchy, State, Identifiable):

    """ This class wraps around strings representing a URI.

    No checks are done, though.
    """

    def __init__(self,
            uri: str,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        Identifiable.__init__(self)
        self.uri = uri

    def __deepcopy__(self, memo):

        """ Create a deepcopy of the object without copying `containingObject`
        """

        cpyid = deepcopy(self.id, memo)

        cpy = Uri(deepcopy(self.uri, memo))
        cpy.id = cpyid
        return cpy


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        if type(self) != type(other):
            return False

        return self.uri == other.uri

    def __str__(self):
        ret_str = "{}".format(self.uri)
        return ret_str


    def searchObject(self, object):

        if not issubclass(type(object), Identifiable):
            return None

        id = object.id
        if self.id == id:
            return self

        return None
