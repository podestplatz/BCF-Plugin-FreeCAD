from interfaces.hierarchy import Hierarchy
from interfaces.identifiable import Identifiable

"""
`elementHierarchy` contains for each element, the writer supports writing, the
hierarchy of the element in its corresponding XML file. Thereby hierarchy is
defined to be the sequence of parents till the root element of the XML document
is reached.
This information is used for adding new elements to the existing XML file.
Keys that contain `@` as second character are attributes that can be changed or
added, all other keys correspond to acutal elements in the XML file.
The first character of every element is the first letter in the name of the
containing element.

"""
elementHierarchy = {"Comment": ["Comment", "Markup"],
    "MViewpoints": ["Viewpoint", "Markup"],
    "TDocumentReference": ["DocumentReference", "Topic", "Markup"],
    "MTopic": ["Topic", "Markup"],
    "TLastModifiedDate": ["LastModifiedDate", "Topic", "Markup"],
    "TLastModifiedAuthor": ["LastModifiedAuthor", "Topic", "Markup"],
    "CLastModifiedDate": ["LastModifiedDate", "Comment", "Markup"],
    "CLastModifiedAuthor": ["LastModifiedAuthor", "Comment", "Markup"],
    "TStage": ["Stage", "Topic", "Markup"],
    "TDueDate": ["DueDate", "Topic", "Markup"],
    "TLabels": ["Labels", "Topic", "Markup"],
    "T@TopicStatus": ["@TopicStatus", "Topic", "Markup"],
    "T@TopicType": ["@TopicType", "Topic", "Markup"],
    }


"""
`elementOrder` contains the relative order of elements in each changeable
parent element. `Comment`, for example, is changeable, but according to the
definition a viewpoint (whose corresponding XML element is `VisualizationInfo`
in `viewpoint.bcfv`) is not changeable, so it doesn't show up in the list
here.
A sequence is defined to be order of elements that are part of a complex type.
For example `Comment` is part of the complex type `Markup`. The sequence of
elements for `Markup` is now: 'Header'->'Topic'->'Comment'->'Viewpoints',
therefore, given `Markup` is defined complete, `Comment` will be third to find
in `Markup`.
"""
elementOrder = {"Markup": ["Header", "Topic", "Comment", "Viewpoints"],
        "Topic": ["ReferenceLink", "Title", "Priority", "Index", "Labels",
            "CreationDate", "CreationAuthor", "ModifiedDate", "ModifiedAuthor",
            "DueDate", "AssignedTo", "Stage", "Description", "BimSnippet",
            "DocumentReference", "RelatedTopic"],
        "Comment": ["Date", "Author", "Comment", "Viewpoint", "ModifiedDate",
            "ModifiedAuthor"]
        }


"""
A list of elements that can occur multiple times in the corresponding XML file
"""
listElements = ["Comment", "DocumentReference", "RelatedTopic", "Labels"]



def getUniqueIdOfListElementInHierarchy(element):

    #TODO: handle labels correctly
    elementHierarchy = hierarchy.Hierarchy.checkAndGetHierarchy(element)
    if not elementHierarchy:
        return None

    listElement = None
    for item in elementHierarchy:
        if item.__class__.__name__ in listElements:
            listElement = item

    if isinstanceof(item, identifiable.Identifiable):
        return item.id
    return None
