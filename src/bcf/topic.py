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


""" Is not used anymore """
class SchemaConstraint:

    """
    Base class for
        - TopicStatus
        - TopicPriority
        - TopicType
        - TopicStage
        - TopicLabel

    This class is not supposed to be instantiated directly. The __init__
    function of every subclass is supposed to parse the contents of the XML
    Schema Definition (XSD) file
    [extension.xsd](https://github.com/buildingSMART/BCF-XML/blob/master/Extension
    Schemas/extension.xsd) and instantiate this base class with a list of valid
    values. Every time the value is to be updated it is checked against the
    list of valid values, which shall not be writable to the outside, and set
    if the new value is in.
    """

    def __init__(self,
            initialValue: str,
            validValues: str):
        self._validValues = validValues
        if initialValue in validValues:
            self._value = initialValue

    @property
    def validValues(self):
        return self._validValues

    @validValues.setter
    def validValues(self, values: List[str]):
        pass # validValues shall not be writable to the outside

    @property
    def value(self):
        return self.value

    @value.setter
    def value(self, newValue: str):

        """
        Only sets if newValue is contained in the list of valid values or,
        if the list is equal to [None] then it also shall be added. Which means
        no restrictions are put upon the value
        """

        if (newValue in self.__validValues or
                self._validValues == [None]):
            self._value = newValue

    @staticmethod
    def parseConstraints(elementName):

        """ Returns a list of the values specified in extensions.xsd for the
        element with the name `elementName`"""

        return [None]


class TopicStatus(SchemaConstraint):

    def __init__(self):

        """
        First gets the valid values from extensions.xsd by calling the
        static method parseConstraints and then initializing the base class
        """

        values = SchemaConstraint.parseConstraints("TopicStatus")
        super(TopicStatus, self).__init__(values[0], values)


class TopicType(SchemaConstraint):

    def __init__(self):

        """
        First gets the valid values from extensions.xsd by calling the
        static method parseConstraints and then initializing the base class
        """

        values = SchemaConstraint.parseConstraints("TopicType")
        super(TopicType, self).__init__(values[0], values)


class TopicLabel(SchemaConstraint):

    def __init__(self):

        """
        First gets the valid values from extensions.xsd by calling the
        static method parseConstraints and then initializing the base class
        """

        values = SchemaConstraint.parseConstraints("TopicLabel")
        super(TopicLabel, self).__init__(values[0], values)


class TopicStage(SchemaConstraint):

    def __init__(self):

        """
        First gets the valid values from extensions.xsd by calling the
        static method parseConstraints and then initializing the base class
        """

        values = SchemaConstraint.parseConstraints("Stage")
        super(TopicStage, self).__init__(values[0], values)


class TopicPriority(SchemaConstraint):

    def __init__(self):

        """
        First gets the valid values from extensions.xsd by calling the
        static method parseConstraints and then initializing the base class
        """

        values = SchemaConstraint.parseConstraints("Priority")
        super(TopicPriority, self).__init__(values[0], values)


class SnippetType(SchemaConstraint):

    def __init__(self):

        """
        First gets the valid values from extensions.xsd by calling the
        static method parseConstraints and then initializing the base class
        """

        values = SchemaConstraint.parseConstraints("SnippetType")
        super(SnippetType, self).__init__(values[0], values)


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
