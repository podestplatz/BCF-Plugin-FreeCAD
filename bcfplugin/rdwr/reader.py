"""
Copyright (C) 2019 PODEST Patrick

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""

import sys
import os
import dateutil.parser
import logging
from zipfile import ZipFile
from xmlschema import XMLSchema
from uuid import UUID
from typing import List, Dict

if __name__ == "__main__":
    sys.path.insert(0, "../")
    print(sys.path)
import bcfplugin
import bcfplugin.util as util
from bcfplugin.rdwr.project import Project
from bcfplugin.rdwr.uri import Uri as Uri
from bcfplugin.rdwr.markup import (Comment, Header, HeaderFile, ViewpointReference, Markup)
from bcfplugin.rdwr.topic import (Topic, BimSnippet, DocumentReference)
from bcfplugin.rdwr.viewpoint import (Viewpoint, Component, Components, ViewSetupHints,
        ComponentColour, PerspectiveCamera, OrthogonalCamera, BitmapFormat,
        Bitmap)
from bcfplugin.rdwr.threedvector import (Point, Line, Direction, ClippingPlane)

SUPPORTED_VERSIONS = ["2.1"]
""" List of BCF versions that are supported by the plugin """

logger = bcfplugin.createLogger(__name__)


def modifyVisinfoSchema(schema):

    """ Alters the FieldOfView restrictions put upon a perspective camera.

    According to the standard applications supporting version 2.1 should be
    able to support fieldOfView values between 0 and 360 degrees.
    """

    # set maximum value
    schema.__dict__["types"].__dict__["target_dict"]["FieldOfView"].__dict__["validators"][1].value = 360
    # set minimum value
    schema.__dict__["types"].__dict__["target_dict"]["FieldOfView"].__dict__["validators"][0].value = 0

    return schema


def extractFileToTmp(zipFilePath: str):

    """
    Extracts the zipFile to the temporary directory of the system.
    """

    zipFile = ZipFile(zipFilePath)

    tmpDir = util.getSystemTmp()
    extractionPath = os.path.join(tmpDir, os.path.basename(zipFilePath))

    logger.debug("Extracting {} to {}".format(zipFile.filename, extractionPath))
    zipFile.extractall(extractionPath)
    return extractionPath


def getVersion(extrBcfPath: str, versionSchemaPath: str):

    """
    Tries to open `extrBcfPath`/bcf.version. If successful it parses it
    into a python dictonary and returns the content of the attribute
    `VersionId` of the element `Version`.

    If `bcf.version` was not found a ValueError is raised. If `bcf.version`
    does not parse against versionSchema then `None` is returned.
    """

    logger.debug("Retrieving version from the BCF project")
    versionFileName = "bcf.version"
    versionFilePath = os.path.join(extrBcfPath, versionFileName)
    if not os.path.exists(versionFilePath):
        raise ValueError("{} was not found in the extracted zip archive {}."\
                "Make sure that you opened a correct bcf zip archive.".format(
                    versionFileName,
                    os.path.basename(extrBcfPath)))

    versionSchema = XMLSchema(versionSchemaPath)
    if not versionSchema.is_valid(versionFilePath):
        return None

    versionDict = versionSchema.to_dict(versionFilePath)
    version = versionDict["@VersionId"]
    logger.debug("Version of the BCF project is {}".format(version))
    return version


def getFileListByExtension(topDir: str, extension: str):

    """
    Returns a list of files in the `topDir` directory that end with `extension`
    """

    fileList = [ f for f in os.listdir(topDir)
                    if os.path.isfile(os.path.join(topDir, f)) ]
    return list(filter(lambda f: f.endswith(extension), fileList))


def getOptionalFromDict(d: Dict, desiredValue: str, empty):

    """
    Returns `d[desiredValue]` if desiredValue is a key of `d`. Otherwise empty
    is returned
    """

    if desiredValue in d:
        return d[desiredValue]
    return empty


########## Object builder functions ##########
"""
Following, all functions prefixed with `build` fulfill the purpose of creating
an object of the class that is specified after `build`. So `buildX` cretes an
object of type `X`.
The data for the object is supplied (in most cases) through a python dictionary.
This dictionary was created by parsing an XML file against an accompanying XSD
through the library `xmlschema`. All functions that expect such a dictionary
further expect the dictonary to be the value of the key value pair that was
generated for the according node from the XML. To make things clearer here a
little example. We will start with the XML file, then show how it is represented
as dictionary by xmlschema and lastly showing what each `buildX` function
expects.

XML
------------------------------
<topNode>
    <comment></comment>
    <comment id=2><author>a@b.c<author></comment>
    <comment id=3></comment>
</topNode>
------------------------------

Python dictonary:
------------------------------
{
    'comment': [None,
                {'@id': 2, 'author': 'a@b.c'},
                {'@id': 3}
               ]
}

buildComment now expects an element of the list value of 'comment'. So either
 - None
 - {'@id': 2, 'author': 'a@b.c'}
 - {'@id': 3}

------------------------------

Note how the keys corresponding to attributes are prefixed
with `@`.

The other type of build functions expect a path to a file. These can be
considered as somewhat top-level `build` functions. They receive the path to an
xml file, as well as a path to the corresponding XSD. They then call the lower
level `build` functions to generate objects of the nodes, if they are complex
enough.
"""

def buildProject(projectFilePath: str, projectSchema: str):

    logger.debug("Building new project object.")
    if projectFilePath is None or projectSchema is None:
        logger.warning("No file and/or no schema file is given.")
        return None
    if not os.path.exists(projectFilePath):
        logger.error("Path of the project file does not exist"\
                " '{}'".format(projectFilePath))
        return None
    if not os.path.exists(projectSchema):
        logger.error("Path of the schema file does not exist"\
                " '{}'".format(projectSchema))
        return None

    schema = XMLSchema(projectSchema)
    (projectDict, errors) = schema.to_dict(projectFilePath, validation="lax")
    errorList = [ str(err) for err in errors ]
    if len(errorList) > 0:
        logger.error(errorList)

    # can do that because the project file is valid and ProjectId is required
    # by the schema
    pId = UUID(projectDict["Project"]["@ProjectId"])
    pName = str()
    pExtensionSchema = str()
    if "Name" in projectDict["Project"]:
        pName = projectDict["Project"]["Name"]
    if "ExtensionSchema" in projectDict:
        pExtensionSchema = projectDict["ExtensionSchema"]

    p = Project(pId, pName, pExtensionSchema)
    logger.debug("New project object created '{}'".format(p))
    return p


def buildComment(commentDict: Dict):

    logger.debug("Building new comment object")
    id = UUID(commentDict["@Guid"])
    commentDate = dateutil.parser.parse(commentDict["Date"]) # parse ISO 8601 datetime
    commentAuthor = commentDict["Author"]

    modifiedAuthor = getOptionalFromDict(commentDict, "ModifiedAuthor", "")
    modifiedDate = getOptionalFromDict(commentDict, "ModifiedDate", None)
    if modifiedDate is not None:
        modifiedDate = dateutil.parser.parse(modifiedDate)

    commentString = commentDict["Comment"] if commentDict["Comment"] else ""

    viewpointRef = getOptionalFromDict(commentDict, "Viewpoint", None)
    if viewpointRef:
        viewpointRef = ViewpointReference(id=UUID(viewpointRef["@Guid"]))

    comment = Comment(id, commentDate, commentAuthor,
            commentString, viewpointRef, modifiedDate, modifiedAuthor)

    logger.debug("New comment object created {}".format(comment))
    return comment


def buildBimSnippet(snippetDict: Dict):

    logger.debug("Building new BimSnippet object")
    reference = Uri(snippetDict["Reference"])
    referenceSchema = Uri(snippetDict["ReferenceSchema"])
    snippetType = snippetDict["@SnippetType"]
    isExternal = getOptionalFromDict(snippetDict, "@isExternal", False)

    bimSnippet = BimSnippet(snippetType, isExternal, reference, referenceSchema)

    logger.debug("New BimSnippet object created {}".format(bimSnippet))
    return bimSnippet


def buildDocRef(docDict: Dict):

    logger.debug("Building new DocumentReference object")
    docUri = getOptionalFromDict(docDict, "ReferencedDocument", None)
    if docUri: # envelope a uri string into an object of Uri
        docUri = Uri(docUri)

    docName = getOptionalFromDict(docDict, "Description", None)
    docId = getOptionalFromDict(docDict, "@Guid", None)
    if docId: #envelope a guid in an UUID object
        docId = UUID(docId)

    docExternal = getOptionalFromDict(docDict, "@isExternal", False)

    docRef = DocumentReference(docId, docExternal, docUri, docName)
    logger.debug("New document reference object created")
    return docRef


def buildTopic(topicDict: Dict):

    logger.debug("Creating new Topic object")
    id = UUID(topicDict["@Guid"])
    title = topicDict["Title"]

    topicDate = dateutil.parser.parse(topicDict["CreationDate"])
    topicAuthor = topicDict["CreationAuthor"]

    topicStatus = getOptionalFromDict(topicDict, "@TopicStatus", "")
    topicType = getOptionalFromDict(topicDict, "@TopicType", "")
    topicPriority = getOptionalFromDict(topicDict, "Priority", "")

    modifiedDate = getOptionalFromDict(topicDict, "ModifiedDate", None)
    if modifiedDate is not None:
        modifiedDate = dateutil.parser.parse(modifiedDate)
    modifiedAuthor = getOptionalFromDict(topicDict, "ModifiedAuthor", "")

    index = getOptionalFromDict(topicDict, "Index", -1)
    dueDate = getOptionalFromDict(topicDict, "DueDate", None)
    if dueDate is not None:
        dueDate = dateutil.parser.parse(dueDate)

    assignee = getOptionalFromDict(topicDict, "AssignedTo", "")
    stage = getOptionalFromDict(topicDict, "Stage", "")
    description = getOptionalFromDict(topicDict, "Description", "")

    bimSnippet = None
    if "BimSnippet" in topicDict:
        bimSnippet = buildBimSnippet(topicDict["BimSnippet"])

    labelList = getOptionalFromDict(topicDict, "Labels", [])

    docRefList = getOptionalFromDict(topicDict, "DocumentReference", [])
    docRefs = [ buildDocRef(docRef) for docRef in docRefList ]

    relatedList = getOptionalFromDict(topicDict, "RelatedTopic", [])
    relatedTopics = [ UUID(relTopic["@Guid"]) for relTopic in relatedList ]

    referenceLinks = getOptionalFromDict(topicDict, "ReferenceLink", [])

    topic = Topic(id, title, topicDate, topicAuthor,
            topicType, topicStatus, referenceLinks,
            docRefs, topicPriority, index,
            labelList, modifiedDate, modifiedAuthor, dueDate,
            assignee, description, stage,
            relatedTopics, bimSnippet)

    logger.debug("New Topic object created")
    return topic


def buildFile(fileDict):

    logger.debug("Building new HeaderFile object")
    filename = getOptionalFromDict(fileDict, "Filename", "")
    filedate = getOptionalFromDict(fileDict, "Date", None)
    if filedate:
        filedate = dateutil.parser.parse(filedate)

    reference = getOptionalFromDict(fileDict, "Reference", "")
    if reference:
        reference = Uri(reference)

    ifcProjectId = getOptionalFromDict(fileDict, "@IfcProject", "")
    if ifcProjectId:
        ifcProjectId = ifcProjectId

    ifcSpatialStructureElement = getOptionalFromDict(fileDict,
            "@IfcSpatialStructureElement", "")
    if ifcSpatialStructureElement:
        ifcSpatialStructureElement = ifcSpatialStructureElement

    isExternal = getOptionalFromDict(fileDict, "@isExternal", True)

    headerfile = HeaderFile(ifcProjectId,
            ifcSpatialStructureElement,
            isExternal,
            filename,
            filedate,
            reference)

    logger.debug("New HeaderFile object created")
    return headerfile


def buildHeader(headerDict):

    logger.debug("Building new Header object")
    filelist = getOptionalFromDict(headerDict, "File", list())
    files = [ buildFile(f) for f in filelist if f is not None ]

    header = Header(files)

    logger.debug("New Header object created")
    return header


def buildViewpointReference(viewpointDict):

    logger.debug("Building new ViewpointReference object")
    id = UUID(viewpointDict["@Guid"])
    viewpointFile = getOptionalFromDict(viewpointDict, "Viewpoint", None)
    if viewpointFile:
        viewpointFile = Uri(viewpointFile)

    snapshotFile = getOptionalFromDict(viewpointDict, "Snapshot", None)
    if snapshotFile:
        snapshotFile = Uri(snapshotFile)

    # -1 denotes a missing index value
    index = getOptionalFromDict(viewpointDict, "Index", -1)

    vpReference = ViewpointReference(id, viewpointFile, snapshotFile, index)

    logger.debug("New ViewpointReference object created")
    return vpReference


def buildSnapshotList(topicDir: str):

    logger.debug("Building SnapshotList")
    isPNG = lambda img: ".png" in img or ".PNG" in img
    snList = list()
    for sn in filter(isPNG, os.listdir(topicDir)):
        snList.append(os.path.join(topicDir, sn))

    logger.debug("New SnapshotList created")
    return snList


def buildMarkup(markupFilePath: str, markupSchemaPath: str):

    logger.debug("Building new Markup object")
    markupSchema = XMLSchema(markupSchemaPath)
    (markupDict, errors) = markupSchema.to_dict(markupFilePath, validation="lax")
    errorList = [ str(err) for err in errors ]
    if len(errorList) > 0:
        logger.error(errorList)

    commentList = getOptionalFromDict(markupDict, "Comment", list())
    comments = [ buildComment(comment) for comment in commentList ]

    topicDict = markupDict["Topic"]
    topic = buildTopic(topicDict)

    headerDict = getOptionalFromDict(markupDict, "Header", None)
    header = None
    # there may be instances that define an empty header element
    if headerDict and len(headerDict) > 0:
        header = buildHeader(headerDict)

    viewpointList = getOptionalFromDict(markupDict, "Viewpoints", list())
    viewpoints = [ buildViewpointReference(vpDict)
                    for vpDict in viewpointList ]

    markupDir = os.path.abspath(os.path.dirname(markupFilePath))
    snapshotList = buildSnapshotList(markupDir)
    markup = Markup(topic, header, comments, viewpoints, snapshotList)

    # Add the right viewpoint references to each comment
    for comment in comments:
        if comment.viewpoint:
            cViewpointRefGuid = comment.viewpoint.xmlId
            viewpointRef = markup.getViewpointRefByGuid(cViewpointRefGuid)
            comment.viewpoint = viewpointRef

    logger.debug("New Markup object created")
    return markup


def buildViewSetupHints(vshDict: Dict):

    logger.debug("Building new ViewSetupHints object")
    spacesVisible = getOptionalFromDict(vshDict, "@SpacesVisible", False)
    spaceBoundariesVisible = getOptionalFromDict(vshDict,
            "@SpaceBoundariesVisible", False)
    openingsVisible = getOptionalFromDict(vshDict, "@OpeningsVisible", False)

    vsh = ViewSetupHints(openingsVisible, spacesVisible,
            spaceBoundariesVisible)
    logger.debug("New ViewSetupHints object created")
    return vsh


def buildComponent(componentDict: Dict):

    logger.debug("Building new Component object")
    id = getOptionalFromDict(componentDict, "@IfcGuid", None) # is no UUID

    authoringToolId = getOptionalFromDict(componentDict,
            "AuthoringToolId", "")

    originatingSystem = getOptionalFromDict(componentDict,
            "OriginatingSystem", "")

    component = Component(id, originatingSystem, authoringToolId)
    logger.debug("New Component object created")
    return component


def buildComponentColour(ccDict: Dict):

    logger.debug("Building new ComponentColour object")
    colour = getOptionalFromDict(ccDict, "@Color", None)
    colourComponents = list()
    cc = None
    if colour: # if a colour is defined then at least one component has to exist
        colourComponentList = [ buildComponent(cp)
                                for cp in ccDict["Component"] ]
        cc = ComponentColour(colour, colourComponentList)


    logger.debug("New ComponentColour object created")
    return cc


def buildComponents(componentsDict: Dict):

    logger.debug("Building new Components object")
    vshDict = getOptionalFromDict(componentsDict, "ViewSetupHints", None)
    vsh = None
    if vshDict:
        vsh = buildViewSetupHints(vshDict)

    componentDict = getOptionalFromDict(componentsDict, "Selection", None)
    sel = list()
    if componentDict:
        componentList = componentDict["Component"]
        sel = [ buildComponent(cpDict) for cpDict in componentList ]

    visibilityDict = componentsDict["Visibility"]
    defaultVisibility = getOptionalFromDict(visibilityDict,
            "@DefaultVisibility", True)

    exceptionDict = getOptionalFromDict(visibilityDict, "Exceptions", None)
    exceptions = list()
    if exceptionDict:
        exceptionList = exceptionDict["Component"] # at least one element has to be present
        exceptions = [ buildComponent(cp) for cp in exceptionList ]

    colourComponentDict = getOptionalFromDict(componentsDict, "Coloring", None)
    componentColours = list()
    if colourComponentDict:
        colourComponentList = colourComponentDict["Color"] # at least one color is required
        componentColours = [ buildComponentColour(ccDict)
                                for ccDict in colourComponentList ]

    components = Components(defaultVisibility, exceptions, sel,
            vsh, componentColours)

    logger.debug("New Components object created")
    return components


def buildPoint(pointDict: Dict):

    logger.debug("Building new Point object")
    return Point(pointDict["X"], pointDict["Y"], pointDict["Z"])


def buildDirection(dirDict: Dict):

    logger.debug("Building new Direction object")
    return Direction(dirDict["X"], dirDict["Y"], dirDict["Z"])


def buildOrthogonalCamera(oCamDict: Dict):

    logger.debug("Building new OrthogonalCamera object")
    camViewpoint = buildPoint(oCamDict["CameraViewPoint"])
    camDirection = buildDirection(oCamDict["CameraDirection"])
    camUpVector = buildDirection(oCamDict["CameraUpVector"])
    vWorldScale = oCamDict["ViewToWorldScale"]

    cam = OrthogonalCamera(camViewpoint, camDirection, camUpVector, vWorldScale)
    logger.debug("New OrthogonalCamera object created")
    return cam


def buildPerspectiveCamera(pCamDict: Dict):

    logger.debug("Building new PerspectiveCamera object")
    camViewpoint = buildPoint(pCamDict["CameraViewPoint"])
    camDirection = buildDirection(pCamDict["CameraDirection"])
    camUpVector = buildDirection(pCamDict["CameraUpVector"])
    fieldOfView = pCamDict["FieldOfView"] # [0, 360] in version 2.1

    cam = PerspectiveCamera(camViewpoint, camDirection, camUpVector,
            fieldOfView)

    logger.debug("New PerspectiveCamera object created")
    return cam


def buildLine(lineDict: Dict):

    logger.debug("Building new Line object")
    start = buildPoint(lineDict["StartPoint"])
    end = buildPoint(lineDict["EndPoint"])

    line = Line(start, end)

    logger.debug("New Line object created")
    return line

def buildClippingPlane(clipDict: Dict):

    logger.debug("Building new ClippingPlane object")
    location = buildPoint(clipDict["Location"])
    direction = buildDirection(clipDict["Direction"])

    cPlane = ClippingPlane(location, direction)

    logger.debug("New ClippingPlane object created")
    return cPlane

def buildBitmap(bmDict: Dict):

    logger.debug("Building new Bitmap object")
    bmFormatStr = bmDict["Bitmap"] # either JPG or PNG
    bmFormat = BitmapFormat.PNG if bmFormatStr == "PNG" else BitmapFormat.JPG

    reference = bmDict["Reference"]
    location = buildPoint(bmDict["Location"])
    normal = buildDirection(bmDict["Normal"])
    up = buildDirection(bmDict["Up"])
    height = bmDict["Height"]

    bitmap = Bitmap(bmFormat, reference, location, normal, up, height)

    logger.debug("New Bitmap object created")
    return bitmap


def buildViewpoint(viewpointFilePath: str, viewpointSchemaPath: str):

    logger.debug("Building new Viewpoint object")
    vpSchema = XMLSchema(viewpointSchemaPath)
    vpSchema = modifyVisinfoSchema(vpSchema)
    (vpDict, errors) = vpSchema.to_dict(viewpointFilePath, validation="lax")
    errorList = [ str(err) for err in errors ]
    if len(errorList) > 0:
        logger.error(errorList)

    id = UUID(vpDict["@Guid"])
    componentsDict = getOptionalFromDict(vpDict, "Components", None)
    components = None
    if componentsDict:
        components = buildComponents(componentsDict)

    oCamDict = getOptionalFromDict(vpDict, "OrthogonalCamera", None)
    oCam = None
    if oCamDict:
        oCam = buildOrthogonalCamera(oCamDict)

    pCamDict = getOptionalFromDict(vpDict, "PerspectiveCamera", None)
    pCam = None
    if pCamDict:
        pCam = buildPerspectiveCamera(pCamDict)

    linesDict = getOptionalFromDict(vpDict, "Lines", None)
    lines = list()
    if linesDict:
        linesList = getOptionalFromDict(linesDict, "Line", list())
        lines = [ buildLine(line) for line in linesList ]

    clippingPlaneDict = getOptionalFromDict(vpDict, "ClippingPlanes", None)
    clippingPlanes = list()
    if clippingPlaneDict:
        clippingPlaneList = getOptionalFromDict(clippingPlaneDict,
                "ClippingPlane", list())
        clippingPlanes = [ buildClippingPlane(clipDict)
                            for clipDict in clippingPlaneList ]

    bitmapList = getOptionalFromDict(vpDict, "Bitmap", list())
    bitmaps = [ buildBitmap(bmDict) for bmDict in bitmapList ]

    viewpoint = Viewpoint(id, components, oCam,
            pCam, lines, clippingPlanes, bitmaps)

    logger.debug("New Viewpoint object created")
    return viewpoint

""" ************ End of build functions ***************** """


def validateFile(validateFilePath: str,
        schemaPath: str,
        bcfFile: str):

    """ Validates `validateFileName` against the XSD file referenced by
    `schemaPath`.

    If successful an empty string is returned, else an error string is
    returned.
    """

    logger.debug("Validating file {} against {}".format(validateFilePath,
        schemaPath))
    schema = XMLSchema(schemaPath)
    try:
        schema.validate(validateFilePath)
    except Exception as e:
        # get parent directory of file, useful for the user if the file is a
        # markup.bcf file inside some topic
        parentDir = os.path.abspath(os.path.join(validateFilePath, os.pardir))
        return "{} file inside {} of {} could not be validated against"\
                " {}\nError:{}".format(validateFilePath, parentDir, bcfFile,
                    os.path.basename(schemaPath), str(e))

    return ""


def readBcfFile(bcfFile: str):

    """ Reads the bcfFile into the memory.

    Before each file is parsed into the class structure it gets validated
    against its corresponding XSD file.  If parsing went successful then a
    value other than a object of type Project is returned.
    """

    logger.debug("Reading file {} and instantiating the data"\
            " model".format(bcfFile))
    tmpDir = util.getSystemTmp()
    (projectSchemaPath, extensionsSchemaPath,\
        markupSchemaPath, versionSchemaPath,\
        visinfoSchemaPath) = util.copySchemas(tmpDir)
    # extensionsSchemaPath is optional and currently not used => does not need
    # to be downloaded.
    if (projectSchemaPath is None or
            markupSchemaPath is None or
            versionSchemaPath is None or
            visinfoSchemaPath is None):
        logger.error("One or more schema files could not be downloaded!"\
                "Please try again in a few moments")
        return None

    bcfExtractedPath = extractFileToTmp(bcfFile)

    # before a file gets read into memory it needs to get validated (i.e.:
    # before the corresponding build* function is called, validate with
    # xmlschema)
    ### Check version ###
    versionFilePath = os.path.join(bcfExtractedPath, "bcf.version")
    if not os.path.exists(versionFilePath):
        logger.error("No bcf.version file found in {}. This file is not optional.")
        return None
    error = validateFile(versionFilePath, versionSchemaPath, bcfFile)
    if error != "":
        logger.error(error)
        return None
    version = getVersion(bcfExtractedPath, versionSchemaPath)
    if version not in SUPPORTED_VERSIONS:
        logger.error("BCF version {} is not supported by this plugin. Supported"\
                "versions are: {}".format(version, SUPPORTED_VERSIONS),
                file=sys.stderr)
        return None

    ### Validate project and build ###
    # project.bcfp is optional, but it is necessary for the data model
    proj = Project(UUID(int=0))
    projectFilePath = os.path.join(bcfExtractedPath, "project.bcfp")
    if os.path.exists(projectFilePath):
        error = validateFile(projectFilePath, projectSchemaPath, bcfFile)
        if error != "":
            msg = ("{} is not completely valid. Some parts won't be"\
                    " available.".format(projectFilePath))
            logger.debug(msg)
            logger.error("{}.\n Following the error"\
                    " message:\n{}".format(msg, error))
        proj = buildProject(projectFilePath, projectSchemaPath)

    ### Iterate over the topic directories ###
    topicDirectories = util.getDirectories(bcfExtractedPath)
    for topic in topicDirectories:
        logger.debug("Topic {} gets builded next".format(topic))
        ### Validate all viewpoint files in the directory, and build them ###
        topicDir = os.path.join(bcfExtractedPath, topic)

        markupFilePath = os.path.join(topicDir, "markup.bcf")
        logger.debug("reading topic {}".format(topicDir))
        error = validateFile(markupFilePath, markupSchemaPath, bcfFile)
        if error != "":
            msg = ("markup.bcf of topic {} does not comply with the standard"
                    " of versions {}."\
                    " Some parts won't be available.".format(topic,
                        SUPPORTED_VERSIONS))
            logger.error(msg)
            logger.error("{}\nError:\n{}".format(msg, error))
        markup = buildMarkup(markupFilePath, markupSchemaPath)

        # generate a viewpoint object for all viewpoints listed in the markup
        # object and add them to the ViewpointReference object (`viewpoint`)
        # inside markup
        for vpRef in markup.viewpoints:
            vpPath = os.path.join(topicDir, vpRef.file.uri)
            try:
                # if some required element was not found, indicated by a key
                # error then skip the viewpoint
                vp = buildViewpoint(vpPath, visinfoSchemaPath)
            except KeyError as err:
                logger.error("{} is required in a viewpoint file."
                    " Viewpoint {}/{} is skipped"\
                        "".format(str(err), topic, vpRef.file))
                continue
            else:
                vpRef.viewpoint = vp

        markup.containingObject = proj
        # add the finished markup object to the project
        proj.topicList.append(markup)

    util.setBcfDir(bcfExtractedPath)
    logger.debug("BCF file is read in and open in"\
            " {}".format(bcfExtractedPath))
    return proj
