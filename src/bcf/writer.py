import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, "/home/patrick/projects/freecad/plugin/src")
    print(sys.path)
import xml.etree.ElementTree as ET
import bcf.reader as reader
from interfaces.hierarchy import Hierarchy
from interfaces.identifiable import Identifiable
from bcf.markup import (Markup, ViewpointReference, Comment, Attribute)

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

    """
    Looks through the hierarchy of an object up to the project. If somewhere on
    the way up an element is identified as list element (may occur more than
    once inside the same XML element) then the id of that element is returned.
    It is assumed that max. one such list element is found. If `element` itself
    is a list element `None` is returned. If no list element is found `None` is
    returned.
    """

    elementHierarchy = Hierarchy.checkAndGetHierarchy(element)
    if not elementHierarchy:
        return None

    listElement = None
    # climb up the hierarchy starting with the direct parent
    for item in elementHierarchy[1:]:
        if item.__class__.__name__ in listElements:
            listElement = item

    if isinstance(listElement, Identifiable):
        return item.id
    return None


def getFileOfElement(element):

    elementHierarchy = Hierarchy.checkAndGetHierarchy(element)
    if not elementHierarchy: # element is not addable
        return None

    strHierarchy = [ item.__class__.__name__ for item in elementHierarchy ]
    if "Viewpoint" in strHierarchy:
        try:
            vpRefIndex = strHierarchy.index("ViewpointReference")
        except Exception as e:
            print("ViewpointReference is not in Hierarchy of Viewpoint",
                    file=sys.stderr)
            raise e
        else:
            viewpointFile = elementHierarchy[vpRefIndex].file
            return viewpointFile
    elif "Markup" in strHierarchy:
        return "markup.bcf"
    elif "Project" in strHierarchy: # it should not come to this point actually
        return "project.bcfp"
    else: # This can only happen if someone wants to change the version file, which is not editable in the plugin
        return None


def getTopicOfElement(element):

    """
    Returns the topic of an element. This is used to generate the right path to
    the file that shall be edited.
    """

    elementHierarchy = Hierarchy.checkAndGetHierarchy(element)
    if not elementHierarchy: # just check for sanity
        return None

    strHierarchy = [ item.__class__.__name__ for item in elementHierarchy ]
    if "Markup" in strHierarchy:
        markupElem = None
        for item in elementHierarchy:
            if isinstance(item, Markup):
                markupElem = item
                break
        return markupElem.topic

    return None


def getIdAttrName(elementId):

    idAttrName = ""
    if isinstance(listElemId, UUID):
        idAttrName = "Guid"
    elif isinstance(listElemId, str):
        idAttrName = "IfcGuid"

    return idAttrName


def getParentElement(element, etRoot):

    elementHierarchy = element.getHierarchyList()
    strHierarchy = [ elem.__class__.__name__ for elem in elementHierarchy ]

    if len(strHierarchy) < 2:
        raise NotImplementedError("Element itself is a root element."\
                "Creating of new files is not supported yet")

    # the topmost element will always be Project
    if strHierarchy[-2] != etRoot.tag:
        print("Root element of hierarchy and root tag of file do not match."\
            " {} != {}".format(strHierarchy[-1], etRoot.tag), file=sys.stderr)

    etParent = None
    listElemId = getUniqueIdOfListElementInHierarchy(element)
    if not listElemId: # parent can be found easily by tag
        etParent = etRoot.find(strHierarchy[1])
        if not etParent and etRoot.tag == strHierarchy[1]:
            etParent = etRoot
    else:
        idAttrName = getIdAttrName(listElementId)
        etParent = etRoot.find(".//*[@{}='{}']".format(idAttrName,
            str(listElemId)))

    return etParent


def getInsertionIndex(element, etParent):

    parentSequence = elementOrder[etParent.tag]
    elemSeqIndex = parentSequence.index(element.xmlName)
    etChildren = [ elem.tag for elem in list(etParent) ]
    revEtChildren = list(reversed(etChildren))
    highestIndex = 0
    for seqElem in parentSequence:
        if seqElem == element.xmlName:
            break

        seqElemIndex = len(etChildren) - 1 - revEtChildren.index(seqElem)
        if seqElemIndex:
            highestIndex = seqElemIndex

    return highestIndex + 1 # ET index starts at 1


def getContainingETElementForAttribute(rootElem, containingElement):

    # candidates are the set of elements that have the same tag as
    # containingElement
    candidates = rootElem.findall(".//{}".format(containingElement.xmlName))
    parentEt = containingElement.getEtElement(
           ET.Element(containingElement.xmlName, {}))
    parentEtChildren = list(parentEt)
    match = None
    # find the right candidate
    for candidate in candidates:
        # check for subelement in the parent whether the equally named
        # subelement in the candidate has the same text, and therefore is equal
        matches = True
        for parentEtChild in parentEtChildren:
            candidateEtChild = candidate.find(
                    ".//{}".format(parentEtChild.tag))
            if candidateEtChild is not None:
                if candidateEtChild.text != parentEtChild.text:
                    matches = False
                    break
            else:
                matches = False
        if matches:
            match = candidate
            break

    return match



def addElement(element):
    fileName = getFileOfElement(element)
    if not fileName:
        raise ValueError("{} is not applicable to be added to anyone"\
            "file".format(element.__class__.__name__))

    if not (".bcfv" in fileName or ".bcf" in fileName):
        raise NotImplementedError("Writing of project.bcfp or bcf.version"\
                " is not yet supported")

    topic = getTopicOfElement(element)
    if not topic:
        raise ValueError("Element of type {} is not contained in a topic."\
            "Cannot be written to file".format(element.__class__.__name__))

    topicDir = topic.id
    bcfDir = reader.bcfDir
    filePath = os.path.join(bcfDir, str(topicDir), fileName)

    xmlTree = ET.parse(filePath)
    if isinstance(element, Attribute):
        parent = element.containingObject
        containingEtElem = getContainingETElementForAttribute(xmlTree.getroot(),
                parent)
        containingEtElem.attrib[element.xmlName] = element.value
    else:
        etParent = getParentElement(element, xmlTree.getroot())
        insertionIndex = getInsertionIndex(element, etParent)
        newEtElement = element.getEtElement(ET.Element(element.xmlName))
        etParent.insert(insertionIndex, newEtElement)

    print("\n\n\nWriting this tree:\n{}".format(ET.dump(xmlTree.getroot())))
    xmlTree.write(filePath, encoding="utf8")


if __name__ == "__main__":
    argFile = "test_data/Issues_BIMcollab_Example.bcf"
    if len(sys.argv) >= 2:
        argFile = sys.argv[1]
    project = reader.readBcfFile(argFile)
    hFiles = project.topicList[0].header.files
    addElement(project.topicList[0].viewpoints[0])
    addElement(project.topicList[0].comments[0])
    hFiles[1].ifcProjectId = "abcdefg"
    hFiles[1].ifcSpatialStructureElement = "abcdefg"
    addElement(hFiles[1]._ifcProjectId)
    addElement(hFiles[1]._ifcSpatialStructureElement)

