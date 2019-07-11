import os
import sys
import urllib.request
import tempfile
import shutil
from enum import Enum
from urllib.error import URLError

from PySide2.QtWidgets import QMessageBox


FREECAD = False
""" Set by BCFPlugin.py when running inside FreeCAD """

GUI = False
""" Set by BCFPlugin.py when running in Gui mode """

errorFile = None
""" File to print errors to """

errorFilePath = ""
""" Path of error file """

DEBUG = False
""" Enables debug outputs """



class Verbosity(Enum):
    EVERYTHING = 1
    NODEBUG = 2
    IMPORTANTERRORS = 3
    INFODEBUG = 4

verbosity = Verbosity.EVERYTHING
if (verbosity == Verbosity.EVERYTHING or verbosity == Verbosity.INFODEBUG):
    # used to inspect the stack to get caller function and caller filename
    import inspect


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

""" Specifies the name of the directory in which the schema files are stored """
schemaDir = "schemas"
""" Holds the paths of the schema files in the plugin directory. Gets set during runtime """
schemaPaths = {} # during runtime this will be a map like __schemaUrls

""" Working directory, here the extracted BCF file is stored """
tempDir = None
def getSystemTmp():

    """
    On first call creates a new temporary directory and returns the absolute
    path to it. On every subsequent call, during the runtime of the
    application, only the once created absolute path is returned.
    """

    global tempDir

    if tempDir is None:
        tempDir = tempfile.TemporaryDirectory()
        #tempDir = tempfile.mkdtemp()

    return tempDir.name
    #return tempDir


def printErr(msg, toFile=False):

    """ Print msg to stderr """

    if not (verbosity == Verbosity.EVERYTHING or
            verbosity == Verbosity.NODEBUG or
            verbosity == Verbosity.IMPORTANTERRORS):
        return

    errmsg = "[ERROR] {}".format(msg)
    if FREECAD:
        import FreeCAD
        FreeCAD.Console.PrintError("{}\n".format(errmsg))
    else:
        print(errmsg, file=sys.stderr)


def printInfo(msg):

    """ Print informative message to the user """

    infomsg = "[INFO] {}".format(msg)
    if FREECAD:
        import FreeCAD
        FreeCAD.Console.PrintMessage("{}\n".format(infomsg))
    else:
        print(infomsg)


def printErrorList(errors, toFile=False):

    """ Print every error message from errors """

    if (verbosity == Verbosity.IMPORTANTERRORS or
            verbosity == Verbosity.INFODEBUG):
        return

    for error in errors:
        printErr(error, toFile)


def showError(msg):

    msgBox = QMessageBox()
    msgBox.critical(None, "ERROR", msg)


def debug(msg):

    """ Prints msg to the default output.

    Default output is determined by FREECAD, if it is set to True then FreeCAD's
    output system is used, Otherwise all messages are printed to stdout/stderr.
    In addition to the message the name of the calling file, as well as the
    functionname of the function that invoked debug is printed, to give context
    to the message.
    """

    if not (verbosity == Verbosity.EVERYTHING or
            verbosity == Verbosity.INFODEBUG):
        return

    callerStackFrame = inspect.stack()[1]
    callerModule = inspect.getmodule(callerStackFrame[0])
    callerModuleName = os.path.basename(callerModule.__file__)
    callerName = inspect.stack()[1].function
    debugmsg = "[DEBUG]{}:{}(): {}".format(callerModuleName, callerName, msg)
    if FREECAD:
        import FreeCAD
        FreeCAD.Console.PrintMessage("{}\n".format(debugmsg))
    else:
        print(debugmsg)


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
