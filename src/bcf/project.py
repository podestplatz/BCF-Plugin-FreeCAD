from uri import Uri
from uuid import UUID
from markup import Markup

class Project:
    def __init__(self,
            uuid: UUID = None,
            name: str = "",
            extSchemaSrc: Uri = None):
        self.id = uuid
        self.name = name
        self.extSchemaSrc = extSchemaSrc
        self.topicList = list()
