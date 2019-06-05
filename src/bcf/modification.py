from datetime import datetime
from interfaces.hierarchy import Hierarchy
from interfaces.state import State

class Modification(Hierarchy, State):

    """
    This class is used by Topic and Comment to for one denote the author
    and date of the last change and the creator and the creation date of an
    object of one of the respective classes
    """

    def __init__(self,
            author: str,
            date: datetime,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        """ Initialisation function for Modification """

        State.__init__(self, state)
        Hierarchy.__init__(self, containingElement)
        self.author = author
        self.date = date


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return self.author == other.author and self.date == other.date


    def __str__(self):

        ret_str = "Modification(author='{}', datetime='{}')".format(self.author,
                self.date)
        return ret_str
