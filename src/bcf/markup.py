from uuid import UUID
from datetime import datetime, date
from uri import Uri
from typing import List # used for custom type annotations
from modification import Modification
from topic import Topic, SnippetType

class Header:
    def __init__(self,
                ifcProjectId: UUID = None,
                ifcSpacialStructureElement: UUID = None,
                external: bool = True,
                filename: str = "",
                time: datetime = None,
                reference: Uri = None):

        """ Initialization function for Header """

        self.ifcProjectId = ifcProjectId
        self.ifcSpacialStructureElement = ifcSpacialStructureElement
        self.external = external
        self.filename = filename
        self.time = time
        self.reference = reference


class ViewpointReference:

    """ Base class for Viewpoint. """

    def __init__(self,
            id: UUID,
            file: Uri = None,
            snapshot: Uri = None,
            index: int = 0):

        """ Initialisation function of ViewpointReference """

        self.id = id
        self.file = file
        self.snapshot = snapshot
        self.index = index


class Comment:

    """ Class holding all data about a comment """

    def __init__(self,
            creation: Modification,
            comment: str,
            viewpoint: ViewpointReference = None,
            lastModification: Modification = None):

        """ Initialisation function of Comment """

        self.creation = creation
        self.comment = comment
        self.viewpoint = viewpoint
        self.lastModification = lastModification


class Markup:

    """ Every topic folder has exactly one markup.bcf file. This forms the
    starting point for the ui to get the data """

    def __init__(self,
            header: Header = None,
            topic: List[Topic] = list(),
            comments: List[Comment] = list(),
            viewpoints: List[ViewpointReference] = list()):

        """ Initialization function for Markup """

        self.header = header
        self.topic = topic
        self.comments = comments
        self.viewpoints = viewpoints

