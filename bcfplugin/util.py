import os
import sys
import urllib.request
import tempfile
import shutil
import logging
from enum import Enum
from urllib.error import URLError

from PySide2.QtWidgets import QMessageBox, QApplication

PREFIX = "bcfplugin_"

errorFile = "{}error.txt".format(PREFIX)
""" File to print errors to """

logInitialized = False
""" Logger object for errors """

MMPI = 25.4
""" Millimeters per inch """

AUTHOR_FILE = "author.txt"
""" Name of the authors file, in which the email address will be stored once per
session """

DIRTY_FILE = "{}dirty.txt".format(PREFIX)
""" Name of the file containing the dirty bit """

""" Specifies the name of the directory in which the schema files are stored """
schemaDir = "schemas"

""" Holds the paths of the schema files in the plugin directory. Gets set during runtime """
schemaPaths = {} # during runtime this will be a map like __schemaUrls

tmpFilePathsFileName = "{}tmp.txt".format(PREFIX)
""" Holds the path to the file that contains just the path to the created
temporary directory """


class Schema(Enum):
    EXTENSION = 1
    VISINFO = 2 # viewpoint info
    MARKUP = 3
    PROJECT = 4
    VERSION = 5

__schemaSrc = "https://raw.githubusercontent.com/buildingSMART/BCF-XML/{0}/{1}Schemas/{2}"
__schemaVersion = "release_2_1"
""" Names of the schema files necessary """
__schemaNames = {
        Schema.EXTENSION: "extensions.xsd",
        Schema.PROJECT: "project.xsd",
        Schema.MARKUP: "markup.xsd",
        Schema.VERSION: "version.xsd",
        Schema.VISINFO: "visinfo.xsd"
        }

""" URLs of the schema files, from where they can be retrieved """
__schemaUrls = {
        Schema.EXTENSION: __schemaSrc.format(__schemaVersion,
            "Extension%20",
            __schemaNames[Schema.EXTENSION]),
        Schema.PROJECT: __schemaSrc.format(__schemaVersion,
            "",
            __schemaNames[Schema.PROJECT]),
        Schema.MARKUP: __schemaSrc.format(__schemaVersion,
            "",
            __schemaNames[Schema.MARKUP]),
        Schema.VERSION: __schemaSrc.format(__schemaVersion,
            "",
            __schemaNames[Schema.VERSION]),
        Schema.VISINFO: __schemaSrc.format(__schemaVersion,
            "",
            __schemaNames[Schema.VISINFO])}


def getTmpFilePath(filename):

    # get platform specific temporary directory
    sysTmp = tempfile.gettempdir()
    filepath = os.path.join(sysTmp, filename)

    return filepath


def appendLineBreak(line):

    if line.endswith("\n"):
        return line
    else:
        return line + "\n"


def storeLine(file, text, lineno):

    """ Replaces the line at `lineno` with the specified `text` in the
    specified `file`.

    `lineno` starts at 1!
    If the file does not contain as many lines as the value of `lineno` blank
    lines are inserted."""

    if not os.path.exists(file): # create the file if does not exist yet
        with open(file, "w") as f: pass

    lines = None
    with open(file, "r") as f:
        lines = f.readlines()

    # it seems like an off by one error, but the last line will be replaced by
    # `text` in the code below
    lineDiff = lineno - len(lines)
    lines = lines + [""]*(lineDiff if lineDiff >= 0 else 0)
    with open(file, "w") as f:
        for line in lines:
            if lines.index(line) == lineno - 1:
                line = text
            f.write(appendLineBreak(line))


def storeTmpPath(tmpPath):

    global tmpFilePathsFileName

    # get platform specific temporary directory
    fpath = getTmpFilePath(tmpFilePathsFileName)

    storeLine(fpath, tmpPath, 1)


def readLine(file, lineno):

    """ Reads the line at `lineno` from `file`.

    `lineno` starts at 1."""

    line = ""
    with open(file, "r") as f:
        lines = [ line.rstrip() for line in f.readlines() ]
        if len(lines) >= lineno:
            line = lines[lineno - 1]
        else:
            line = None

    return line


def getSystemTmp(createNew: bool = False):

    """ Creates a temporary directory on first call or if `createNew` is set.

    On subsequent calls the temp dir that was created latest is returned
    """

    global tmpFilePathsFileName
    global PREFIX

    tmpDir = ""
    fpath = getTmpFilePath(tmpFilePathsFileName)
    if not os.path.exists(fpath):
        tmpDir = tempfile.mkdtemp(prefix=PREFIX)
        storeLine(fpath, tmpDir, 1)

    else:
        tmpDir = readLine(fpath, 1)

    return tmpDir


def setBcfDir(dir):

    global tmpFilePathsFileName

    fpath = getTmpFilePath(tmpFilePathsFileName)
    # fpath is assumed to already exist when this function is called the first
    # time

    storeLine(fpath, dir, 2)


def getBcfDir():

    global tmpFilePathsFileName

    fpath = getTmpFilePath(tmpFilePathsFileName)
    bcfDir = readLine(fpath, 2)

    return bcfDir


def deleteTmp():

    """ Delete the temporary directory with all its contents """

    global PREFIX

    sysTmp = tempfile.gettempdir()
    for fname in os.listdir(sysTmp):
        if fname.startswith(PREFIX):
            fpath = os.path.join(sysTmp, fname)
            if os.path.isdir(fpath):
                shutil.rmtree(fpath)
            elif os.path.isfile(fpath):
                os.remove(fpath)
            else:
                # special file, like socket
                pass


def getCurrentQScreen():

    """ Return a reference to the QScreen object associated with the screen the
    application is currently running on. """

    from PySide2.QtWidgets import QMessageBox, QApplication

    desktop = QApplication.desktop()
    screenNumber = desktop.screenNumber()

    return QApplication.screens()[screenNumber]


def isAuthorSet():

    """ Checks for author.txt file in temp directory.

    author.txt will be filled once per session with the email address of the
    author. It is then used as value for the "ModifiedAuthor" fields in the data
    model.
    """

    authorsPath = os.path.join(getSystemTmp(), AUTHOR_FILE)
    if os.path.exists(authorsPath):
        return True
    return False


def setAuthor(author: str):

    """ Creates the authors file in the temporary directory with `author` as
    content.

    If the file already exists, then the file is just overwritten.
    """

    authorsPath = os.path.join(getSystemTmp(), AUTHOR_FILE)
    with open(authorsPath, "w") as f:
        f.write(author)


def getAuthor():

    """ Reads the contents of AUTHORS_FILE and returns its contents.

    If the file does not exist `None` is returned. This function assumes that
    the file only contains one line, without a line break, containing the
    author's email.
    """

    authorsPath = os.path.join(getSystemTmp(), AUTHOR_FILE)
    if not os.path.exists(authorsPath):
        return None

    author = ""
    with open(authorsPath, "r") as f:
        author = f.read()

    return author


def retrieveWebFile(schema: Schema, storePath: str):

    """
    Tries to retrieve the XML Schema Definition file, identified by `schema`
    from the url stored in `__schemaUrls`. If the file could be loaded it is
    stored at `storePath`.
    Returns `None` if an error occurs or the path of the written file if
    successful.
    """

    fileUrl = __schemaUrls[schema]
    try:
        with urllib.request.urlopen(fileUrl) as response:
            schemaContent = response.read()
            with open(storePath, "wb+") as file:
                file.write(schemaContent)
    except URLError as e:
        print("Here is the stack trace {}".format(str(e)), file=sys.stderr)
        print("Could not retrieve {}".format(fileUrl), file=sys.stderr)
        return None
    except Exception as e:
        print("Error occured: {}".format(str(e)), file=sys.stderr)
        return None
    else:
        return storePath


def downloadToDir(dirPath: str):

    """
    Downloads all schema files, specified in `__schemaUrls` to the specified
    directory `dirPath`
    """

    projectSchemaPath = retrieveWebFile(Schema.PROJECT,
            os.path.join(dirPath, "project.xsd"))
    extensionsSchemaPath = retrieveWebFile(Schema.EXTENSION,
            os.path.join(dirPath, "extensions.xsd"))
    markupSchemaPath = retrieveWebFile(Schema.MARKUP,
            os.path.join(dirPath, "markup.xsd"))
    versionSchemaPath = retrieveWebFile(Schema.VERSION,
            os.path.join(dirPath, "version.xsd"))
    visinfoSchemaPath = retrieveWebFile(Schema.VISINFO,
            os.path.join(dirPath, "visinfo.xsd"))

    return (projectSchemaPath, extensionsSchemaPath,
            markupSchemaPath, versionSchemaPath,
            visinfoSchemaPath)


def getDirectories(topDir: str):

    """
    Returns a list of all directories that are subdirectories of `topDir`.
    """

    subdirs = list()
    for (dirpath, dirnames, filenames) in os.walk(topDir):
        subdirs = dirnames
        break
    return subdirs


def setSchemaPaths(rootPath: str):

    """
    Fill `schemaPaths` with the paths of the respective schema file, located in
    `rootPath/schema`
    """

    global schemaPaths

    schemaDirPath = os.path.join(rootPath, schemaDir)

    schemaPaths[Schema.EXTENSION] = os.path.join(schemaDirPath,
            __schemaNames[Schema.EXTENSION])
    schemaPaths[Schema.PROJECT] = os.path.join(schemaDirPath,
            __schemaNames[Schema.PROJECT])
    schemaPaths[Schema.MARKUP] = os.path.join(schemaDirPath,
            __schemaNames[Schema.MARKUP])
    schemaPaths[Schema.VERSION] = os.path.join(schemaDirPath,
            __schemaNames[Schema.VERSION])
    schemaPaths[Schema.VISINFO] = os.path.join(schemaDirPath,
            __schemaNames[Schema.VISINFO])


def updateSchemas(rootPath: str):

    """
    Schema files are located in PLUGIN_ROOT/src/schemas/.
    Here it is expected that `rootPath == PLUGIN_ROOT`.

    The above mentioned path is created if not present. All schema files will be
    retrieved using `retrieveWebFile` and stored in `rootPath/schemas`
    """

    schemaDirPath = os.path.join(rootPath, schemaDir)
    if not os.path.exists(schemaDirPath):
        os.mkdir(schemaDirPath)

    (projectSchemaPath, extensionsSchemaPath,\
        markupSchemaPath, versionSchemaPath,\
        visinfoSchemaPath) = downloadToDir(schemaDirPath)

    setSchemaPaths(rootPath)


def copySchemas(dstDir: str):

    """
    Copies the schema files, located in PLUGIN_ROOT/src/schemas/ to the given
    `dstDir` directory.

    If prior to this function call no schema files were downloaded, the download
    is automatically started.
    """

    rootPath = os.path.realpath(__file__)
    rootPath = rootPath.replace("util.py", "")
    schemaDirPath = os.path.join(rootPath, schemaDir)
    if not os.path.exists(schemaDirPath):
        updateSchemas(rootPath)
    else:
        setSchemaPaths(rootPath)

    dstSchemaPaths = {}
    for key in schemaPaths.keys():
        dstSchemaPaths[key] = os.path.join(dstDir, __schemaNames[key])
        shutil.copyfile(schemaPaths[key], os.path.join(dstDir, __schemaNames[key]))

    return (dstSchemaPaths[Schema.PROJECT], dstSchemaPaths[Schema.EXTENSION],
        dstSchemaPaths[Schema.MARKUP], dstSchemaPaths[Schema.VERSION],
        dstSchemaPaths[Schema.VISINFO])


def doesFileExistInProject(file: str):

    """ Check whether the `file` exists in the currently opened project.

    `file` is assumed to be a relative path, starting from the root of the
    BCFFile. Thus having a maximum depth of 2.
    """

    global tempdir

    fileAbsPath = os.path.join(tempdir, file)
    return os.path.exists(fileAbsPath)


def setDirty(bit: bool):

    global DIRTY_FILE

    filepath = getTmpFilePath(DIRTY_FILE)

    with open(filepath, "w") as f:
        if bit:
            f.write("True")
        else:
            f.write("False")


def getDirtyBit():

    global DIRTY_FILE

    filepath = getTmpFilePath(DIRTY_FILE)
    if not os.path.exists(filepath):
        return False

    bit = False
    with open(filepath, "r") as f:
        content = f.read()
        if content == "True":
            bit = True
        else:
            bit = False
    return bit


def loggingReady():

    return logInitialized


def initializeErrorLog():

    global logInitialized

    if not logInitialized:
        errFilePath = getTmpFilePath(errorFile)
        logging.basicConfig(filename=errFilePath,
                level=logging.ERROR)
        logInitialized = True


class cd:

    """ Context manager for changing working directory """

    def __init__(self, newDir):
        self.newDir = os.path.expanduser(newDir)

    def __enter__(self):
        self.saveDir = os.getcwd()
        os.chdir(self.newDir)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saveDir)


if __name__ == "__main__":
    for key in __schemaUrls:
        retrieveWebFile(key, "test{}".format(str(key)))
    try:
        (valid, error) = schemaValidate("testSchema.PROJECT", "project.bcfp")
    except ValueError as e:
        print("One of the files does not exist. Here is the stack trace:\
                {}".format(str(e)))
    if valid:
        print("File is valid")
    else:
        print("File is not valid because:\n{}".format(error))
