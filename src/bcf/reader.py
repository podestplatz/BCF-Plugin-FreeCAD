import sys
import os
import util
import project
from zipfile import ZipFile
from xmlschema import XMLSchema
from uuid import UUID

DEBUG = True

if DEBUG:
    import pprint

def getSystemTmp():

    """
    Depending on the system, the correct temporary folder is returned as string
    """

    if os.name == "nt":
        return "C:\\Temp"
    else:
        return "/tmp/"

def readFile(path: str):

    """
    Tries to open the supplied file (`path`) and returns the ZipFile object.
    If an exception is raised `None` is returned.
    """

    if not os.path.exists(str):
        raise ValueError

    file = None
    try:
        file = ZipFile(path)
    except Exception as e:
        print("The supplied BCF file ({}) could not be opened.\nError:\
                {}".format(path, str(e)))
        return None

    return file

def getDirectories(zipFile: ZipFile):

    """
    Reads out all directory names that are in the zipFile and returns a list of
    strings, where each string represents the name of one directory.
    """

    if zipFile is None:
        raise ValueError

    zipDirectories = list()
    for member in zipFile.infolist():
        if member.filename[-1:] == "/":
            zipDirectories.append(member.filename)

    return zipDirectories

def openProject(zipFile: ZipFile):

    """
    Looks for a project.bcfp file and returns a file handle if found
    """

    if zipFile is None:
        raise ValueError

    projectFileInfo = [ member for member in zipFile.infolist()
                    if "project.bcfp" in member.filename]

    if projectFileInfo is not []:
        return zipFile.open(projectFileInfo[0].filename)
    return None


def schemaValidate(schemaPath: str, xmlFile: str):

    """
    Takes the schemaFile and loads it into the module xmlschema. With the
    resulting object `xmlFile` is checked whether it adheres to the
    specification or not.
    Returns a tuple: first element is a boolean value, and the second is a
    string containing the error message.
    """

    if not (os.path.exists(schemaPath) or os.path.exists(xmlFile)):
        raise ValueError

    schema = XMLSchema(schemaPath)
    valid = schema.is_valid(xmlFile)
    print("validating {} against {}".format(xmlFile, schemaPath))
    if valid:
        return (valid, "")
    else:
        try:
            # it is going to fail. I want the error message to return it
            schema.validate(xmlFile)
        except Exception as e:
            return (valid, str(e))


def extractFileToTmp(zipFile: ZipFile, memberName: str):

    """
    Tries to extract the file or directory with the name `memberName` from the
    given zipFile `zipFile` into a temporary directory. If successful the path
    to the file is returned, otherwise None is returned.
    """

    if not memberName in zipFile.namelist():
        raise FileNotFoundError("'{}' is not part of the supplied zip archive"\
            " {}. Make sure that it is a correct bcf"\
            " archive!".format(memberName, zipFile.filename))

    extractionPath = getSystemTmp()
    filePath = str()
    try:
        filePath = zipFile.extract(memberName, extractionPath)
    except Exception as e:
        print("Error during extracting '{}' to"\
                " {}".format(memberName, extractionPath))
        print("Make sure that '{}' exists exactly like that in the zipFile "\
                "and does not reside in any additional"\
                " subdirectory".format(memberName))
        return None

    return filePath


def getVersion(zipFile: ZipFile, versionSchemaPath: str):

    """
    Searches for the `bcf.version` member in the zip file `zipFile`. If found
    it parses it into a python dictonary and returns the content of the
    attribute `VersionId` of the element `Version`.

    If `bcf.version` was not found a ValueError is raised. If `bcf.version`
    does not parse against versionSchema then `None` is returned.
    """

    versionFileName = "bcf.version"
    if not "bcf.version" in zipFile.namelist():
        raise ValueError("{} was not found in the zip archive {}. Make sure"\
                " that it is a correct bcf zip" \
                " archive.".format(versionFileName, zipFile.filename))

    try:
        versionFilePath = extractFileToTmp(zipFile, versionFileName)
    except FileNotFoundError as e:
        print("It appears that {} is not a valid BCF archive.")
        print(str(e))
        raise FileNotFoundError(str(e))

    versionSchema = XMLSchema(versionSchemaPath)
    if not versionSchema.is_valid(versionFilePath):
        return None

    versionDict = versionSchema.to_dict(versionFilePath)
    if DEBUG:
        pprint.pprint(versionDict)
    return versionDict["@VersionId"]


########## Object builder functions ##########

def buildProject(zipFile: ZipFile, projectSchema: str):

    """
    Parses the contents of the project.bcfv file from inside the ZipFile.
    First the XML file is parsed into a python dictionary using
    xmlschema.XMLSchema.to_dict(xmlFilePath). Then this python dictionary is morphed
    into an objec of the Project class.

    Due to limitations of the xmlschema library, project.bcfp is first
    extracted into a temporary location.
    """

    projectFileName = "project.bcfp"
    # Assumption: it is already validated that the BCF file (`zipFile`)
    # contains the project.bcfp file
    projectFilePath = extractFileToTmp(zipFile, projectFileName)

    if projectFilePath is None:
        return None

    schema = XMLSchema(projectSchema)
    projectDict = schema.to_dict(projectFilePath)

    if DEBUG:
        pprint.pprint(projectDict)

    # can do that because the project file is valid and ProjectId is required
    # by the schema
    pId = UUID(projectDict["Project"]["@ProjectId"])
    pName = str()
    pExtensionSchema = str()
    if "Name" in projectDict["Project"]:
        pName = projectDict["Project"]["Name"]
    if "ExtensionSchema" in projectDict:
        pExtensionSchema = projectDict["ExtensionSchema"]

    p = project.Project(pId, pName, pExtensionSchema)
    return p


if __name__ == "__main__":
    projectSchemaPath = "/tmp/project.xsd"
    versionSchemaPath = "/tmp/version.xsd"
    util.retrieveWebFile(util.Schema.PROJECT, projectSchemaPath)
    util.retrieveWebFile(util.Schema.VERSION, versionSchemaPath)
    with ZipFile(sys.argv[1]) as zipFile:
        bcfVersion = getVersion(zipFile, versionSchemaPath)
        project = buildProject(zipFile, projectSchemaPath)
        print(project)
        print("The version of the bcf file is {}".format(bcfVersion))
