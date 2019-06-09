import bcf.util
from typing import List
from enum import Enum
from uuid import UUID
from datetime import date
from xmlschema import XMLSchema
from bcf.modification import Modification
from bcf.uri import Uri
from interfaces.hierarchy import Hierarchy
from interfaces.identifiable import Identifiable
from interfaces.state import State
from interfaces.xmlname import XMLName


class DocumentReference(Hierarchy, Identifiable, State, XMLName):
    def __init__(self,
                id: UUID = None,
                external: bool = False,
                reference: Uri = None,
                description: str = "",
                containingElement = None,
                state: State.States = State.States.ORIGINAL):

        """ Initialization function for DocumentReference """

        Hierarchy.__init__(self, containingElement)
        Identifiable.__init__(self, id)
        State.__init__(self, state)
        XMLName.__init__(self)
        self.external = external
        self.reference = reference
        self.description = description


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.id == other.id and
                self.external == other.external and
                self.reference == other.reference and
                self.description == other.description)


    def __str__(self):
        str_ret = ("DocumentReference(id={}, external={}, reference={},"\
            " description={})").format(self.id, self.external, self.reference,
                self.description)

        return str_ret


class BimSnippet(Hierarchy, State, XMLName):
    def __init__(self,
            type: SnippetType = None,
            external: bool = False,
            reference: Uri = None,
            schema: Uri = None,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        """ Initialization function for BimSnippet """

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        XMLName.__init__(self)
        self.type = type
        self.external = external
        self.reference = reference
        self.schema = schema


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.type == other.type and
                self.external == other.external and
                self.reference == other.reference and
                self.schema == other.schema)


class Labels(list, Hierarchy, XMLName):

    def __init__(self, data=[], containingElement = None):

        list.__init__(self, data)
        Hierarchy.__init__(self, containingElement)
        XMLName.__init__(self)


class Topic(Hierarchy, Identifiable, State, XMLName):

    """ Topic contains all metadata about one ... topic """

    def __init__(self,
            id: UUID,
            title: str,
            creation: Modification,
            type: str = "",
            status: str = "",
            refs: List[DocumentReference] = list(),
            priority: str = "",
            index: int = 0,
            labels: List[str] = list(),
            lastModification: Modification = None,
            dueDate: date = None,
            assignee: str = "",
            description: str = "",
            stage: str = "",
            relatedTopics: List[UUID] = [],
            bimSnippet: BimSnippet = None,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        """ Initialisation function of Topic """

        Hierarchy.__init__(self, containingElement)
        Identifiable.__init__(self, id)
        State.__init__(self, state)
        XMLName.__init__(self)
        self.title = title
        self.creation = creation
        self.type = type
        self.status = status
        self.refs = refs
        self.priority = priority
        self.index = index
        self.labels = Labels(labels, self)
        self.lastModification = lastModification
        self.dueDate = dueDate
        self.assignee = assignee
        self.description = description
        self.stage = stage
        self.relatedTopics = relatedTopics
        self.bimSnippet = bimSnippet


    def __checkNone(self, this, that):

        equal = False
        if this and that:
            equal = this == that
        elif (this is None and that is None):
            equal = True
        return equal


    def __printEquality(self, equal, name):

        if not equal:
            print("{} is not equal".format(name))


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        self.__printEquality(self.id == other.id, "id")
        self.__printEquality(self.title == other.title, "title")
        self.__printEquality(self.__checkNone(self.creation, other.creation),
                "creation")
        self.__printEquality(self.type == other.type, "type")
        self.__printEquality(self.status == other.status, "status")
        self.__printEquality(self.refs == other.refs, "refs")
        self.__printEquality(self.priority == other.priority, "priority")
        self.__printEquality(self.index == other.index, "index")
        self.__printEquality(self.labels == other.labels, "labels")
        self.__printEquality(self.assignee == other.assignee, "assignee")
        self.__printEquality(self.description == other.description, "description")
        self.__printEquality(self.stage == other.stage, "stage")
        self.__printEquality(self.relatedTopics == other.relatedTopics,
                "relatedTopics")
        self.__printEquality(self.__checkNone(self.lastModification,
            other.lastModification), "lastModification")
        self.__printEquality(self.__checkNone(self.dueDate,
            other.dueDate), "dueDate")
        self.__printEquality(self.__checkNone(self.bimSnippet,
            other.bimSnippet), "bimSnippet")

        return (self.id == other.id and
                self.title == other.title and
                self.__checkNone(self.creation, other.creation) and
                self.type == other.type and
                self.status == other.status and
                self.refs == other.refs and
                self.priority == other.priority and
                self.index == other.index and
                self.labels == other.labels and
                self.__checkNone(self.lastModification, other.lastModification) and
                self.__checkNone(self.dueDate, other.dueDate) and
                self.assignee == other.assignee and
                self.description == other.description and
                self.stage == other.stage and
                self.relatedTopics == other.relatedTopics and
                self.bimSnippet == other.bimSnippet)

    def __str__(self):
        import pprint
        doc_ref_str = "None"
        if self.refs:
            doc_ref_str = "["
            for doc_ref in self.refs:
                doc_ref_str += str(doc_ref)
            doc_ref_str += "]"

        str_ret = """---- Topic ----
    ID: {},
    Title: {},
    Creation: {}
    Type: {},
    Status: {},
    Priority: {},
    Index: {},
    Modification: {},
    DueDate: {},
    AssignedTo: {},
    Description: {},
    Stage: {},
    RelatedTopics: {},
    Labels: {},
    DocumentReferences: {}""".format(self.id, self.title, str(self.creation),
            self.type, self.status, self.priority, self.index,
            str(self.lastModification), self.dueDate,
            self.assignee, self.description, self.stage, self.relatedTopics,
            self.labels, doc_ref_str)
        return str_ret
