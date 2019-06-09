from uuid import UUID
from bcf.uri import Uri
from interfaces.hierarchy import Hierarchy
from interfaces.state import State
from interfaces.xmlname import XMLName

class Project(Hierarchy, State, XMLName):
    def __init__(self,
            uuid: UUID,
            name: str = "",
            extSchemaSrc: Uri = None,
            state: State.States = State.States.ORIGINAL):

        """ Initialisation function of Project """

        Hierarchy.__init__(self, None) # Project is the topmost element
        State.__init__(self, state)
        XMLName.__init__(self)
        self.id = uuid
        self.name = name
        self.extSchemaSrc = extSchemaSrc
        self.topicList = list()

    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        if type(self) != type(other):
            return False

        return self.id == other.id \
            and self.name == other.name \
            and self.extSchemaSrc == other.extSchemaSrc \
            and self.topicList == other.topicList


    def __str__(self):

        ret_str = """Project(
id='{}',
name='{}',
extSchemaSrc='{}',
topicList='{}')""".format(self.id, self.name, self.extSchemaSrc,
                self.topicList)
        return ret_str
