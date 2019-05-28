from uri import Uri
from uuid import UUID
from markup import Markup

class Project:
    def __init__(self,
            uuid: UUID,
            name: str = "",
            extSchemaSrc: Uri = None):

        """ Initialisation function of Project """

        self.id = uuid
        self.name = name
        self.extSchemaSrc = extSchemaSrc
        self.topicList = list()

    def __eq__(self, other):
        return self.id == other.id \
            and self.name == other.name \
            and self.extSchemaSrc == other.extSchemaSrc \
            and self.topicList == other.topicList
