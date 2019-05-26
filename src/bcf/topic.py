from typing import List
from enum import Enum
from uuid import UUID
from modification import Modification
from uri import Uri
from datetime import date

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
        self.validValues = validValues
        if initialValue in validValues:
            self.value = initialValue

    @property
    def validValues(self):
        return self.validValues

    @validValues.setter
    def validValues(self, values: List[str]):
        pass # validValues shall not be writable to the outside

    @property
    def value(self):
        return self.value

    @value.setter
    def value(self, newValue: str):

        """ Only sets if newValue is valid """

        if newValue in self.__validValues:
            self.value = newValue

    @staticmethod
    def parseConstraints(self, elementName):

        """ Returns a list of the values specified in extensions.xsd for the
        element with the name `elementName`"""

        #TODO: write that function

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


class Topic:

    """ Topic contains all metadata about one ... topic """

    def __init__(self,
            id: UUID,
            title: str,
            creation: Modification,
            type: TopicType = None,
            status: TopicStatus = None,
            refs: List[Uri] = list(),
            priority: TopicPriority = None,
            index: int = 0,
            labels: List[str] = list(),
            lastModification: Modification = None,
            dueDate: date = None,
            assignee: str = "",
            description: str = "",
            stage: TopicStage = None):

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

