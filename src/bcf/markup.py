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

class DocumentReference:
    def __init__(self,
                id: UUID = None,
                external: bool = False,
                reference: Uri = None,
                description: str = ""):

        """ Initialization function for DocumentReference """

        self.id = id
        self.external = external
        self.reference = reference
        self.description = description


class BimSnippet:
    def __init__(self,
            type: SnippetType = None,
            external: bool = True,
            reference: Uri = None,
            schema: Uri = None):

        """ Initialization function for BimSnippet """

        self.type = type
        self.external = external
        self.reference = reference
        self.schema = schema


class ViewpointReference:

    """ Base class for Viewpoint. """

    def __init__(self,
            file: Uri = None,
            snapshot: Uri = None,
            index: int = 0):

        """ Initialisation function of ViewpointReference """

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
            bimSnippet: BimSnippet = None,
            docRefs: List[DocumentReference] = list(),
            relatedTopic: UUID = None,
            comments: List[Comment] = list(),
            viewpoints: List[ViewpointReference] = list(),
            snapshots: List[Uri] = list()):

        """ Initialization function for Markup """

        self.header = header
        self.topic = topic
        self.bimSnippet = bimSnippet
        self.docRefs = docRefs
        self.relatedTopic = relatedTopic
        self.comments = comments
        self.viewpoints = viewpoints
        self.snapshots = snapshots

