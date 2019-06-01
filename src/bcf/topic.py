import bcf.util
from typing import List
from enum import Enum
from uuid import UUID
from datetime import date
from xmlschema import XMLSchema
from bcf.modification import Modification
from bcf.uri import Uri


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


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.id == other.id and
                self.external == other.external and
                self.reference == other.reference and
                self.description == other.description)


class BimSnippet:
    def __init__(self,
            type: SnippetType = None,
            external: bool = False,
            reference: Uri = None,
            schema: Uri = None):

        """ Initialization function for BimSnippet """

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


class Topic:

    """ Topic contains all metadata about one ... topic """

    def __init__(self,
            id: UUID,
            title: str,
            creation: Modification,
            type: str = None,
            status: str = None,
            refs: List[DocumentReference] = list(),
            priority: str = None,
            index: int = 0,
            labels: List[str] = list(),
            lastModification: Modification = None,
            dueDate: date = None,
            assignee: str = "",
            description: str = "",
            stage: str = None,
            relatedTopics: List[UUID] = None):

        """ Initialisation function of Topic """

        self.id = id
        self.title = title
        self.creation = creation
        self.type = type
        self.status = status
        self.refs = refs
        self.priority = priority
        self.index = index
        self.labels = labels
        self.lastModification = lastModification
        self.dueDate = dueDate
        self.assignee = assignee
        self.description = description
        self.stage = stage
        self.relatedTopics = relatedTopics


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.id == other.id and
                self.title == other.title and
                self.creation == other.creation and
                self.type == other.type and
                self.status == other.status and
                self.refs == other.refs and
                self.priority == other.priority and
                self.index == other.index and
                self.labels == other.labels and
                self.lastModification == other.lastModification and
                self.dueDate == other.dueDate and
                self.assignee == other.assignee and
                self.description == other.description and
                self.stage == other.stage and
                self.relatedTopics == other.relatedTopics)

