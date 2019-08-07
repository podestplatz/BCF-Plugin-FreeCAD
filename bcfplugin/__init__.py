import os
import sys
import logging
import importlib
excPath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, excPath)

__all__ = ["programmaticInterface.py", "ui"]

FREECAD = False
""" Set by BCFPlugin.py when running inside FreeCAD """

GUI = False
""" Set by BCFPlugin.py when running in Gui mode """

TMPDIR = None
""" Temp directory used by the plugin as working directory """

DIRTY = False
""" Denotes whether there are unwritten changes in the data model """

PROJDIR = None
""" The directory into which the bcf file is extracted to """

dependencies = ["dateutil", "pytz", "pyperclip", "xmlschema"]
""" Packages this plugin depends on. """

LOGFORMAT = "%(levelname)s:%(module)s.%(funcName)s() - %(message)s"
""" Format of all logged messages """


def printErr(msg):

    global FREECAD

    if FREECAD:
        FreeCAD.Console.PrintError(msg)
    else:
        print(msg, file=sys.stderr)


def printInfo(msg):

    global FREECAD

    if FREECAD:
        FreeCAD.Console.PrintMessage(msg)
    else:
        print(msg)


def getStdoutHandler():

    """ Returns a handler for the logging facility of python, writing the
    messages to stdout """

    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)

    format = logging.Formatter(LOGFORMAT)
    handler.setFormatter(format)

    return handler


def getFileHandler(fpath):

    """ Returns a handler for the logging facility of python, writing the
    messages to file `fpath` """

    handler = logging.FileHandler(fpath)
    handler.setLevel(logging.DEBUG)

    format = logging.Formatter(LOGFORMAT)
    handler.setFormatter(format)

    return handler


def check_dependencies():
    available = True

    for dependency in dependencies:
        try:
            importlib.import_module(dependency)
        except Exception as e:
            pkg = dependency
            available = False
            break

    if not available:
        printErr("Could not find the module `{}`. Install it through"\
                " pip\n\tpip install {}\nYou also might want to"\
                " install it in a virtual environment. To create and initialise"\
                " said env execute\n\tpython -m venv <NAME>\n\tsource"\
                " ./<NAME>/bin/activate".format(pkg, pkg))
        printInfo("If you already have it installed inside a virtual environment" \
                ", no problem we just need to modify the `sys.path` variable a"\
                " bit. python inside FreeCAD, unfortunately, is not aware by" \
                " default, of a virtual environment. To do that you have to " \
                " execute a few steps:\n"\
                "\t1. find the folder in which your venv is located,\n"\
                "\t2. find out with which python version FreeCAD was compiled,\n"\
                "\t3. execute `sys.path.append('/path/to/venv/lib/python<VERSION>/site-packages')`"\
                "\nIf that fails, try to run `import sys` and execute it"\
                " again.")
    return available



# detection if this script is run inside FreeCAD
try:
    import FreeCAD
except:
    pass
else:
    FREECAD = True
    if FreeCAD.GuiUp:
        FreeCAD.Console.PrintMessage("set util.GUI\n")
        import FreeCADGui as FGui
        GUI = True


frontend = None
if not check_dependencies():
    raise ImportError

import util
util.deleteTmp()
from programmaticInterface import *
