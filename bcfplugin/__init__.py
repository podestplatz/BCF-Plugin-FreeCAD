import os
import sys
excPath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, excPath)

__all__ = ["programmaticInterface.py", "ui"]

TMPDIR = None
""" Temp directory used by the plugin as working directory """

FREECAD = False
GUI = False

def printErr(msg):

    global FREECAD

    if FREECAD:
        FreeCAD.Console.PrintError(msg)
    else:
        print(msg, file=sys.stderr)


def printInfo(msg):

    global FREECAD

    if FREECAD:
        FreeCAD.Console.PrintInfo(msg)
    else:
        print(msg)


def check_dependencies():
    available = True
    try:
        import dateutil
    except:
        pkg = "dateutil"
        available = False

    if available:
        try:
            import xmlschema
        except:
            pkg = "xmlschema"
            available = False

    if available:
        try:
            import pytz
        except:
            pkg = "pytz"
            available = False

    if not available:
        printErr("Could not find the module `xmlschema`. Install it through"\
                " pip\n\tpip install {}\nYou also might want to"\
                " install it in a virtual environment. To create and initialise"\
                " said env execute\n\tpython -m venv <NAME>\n\tsource"\
                " ./<NAME>/bin/activate".format(pkg))
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
    import util
    util.FREECAD = True
    FREECAD = True
    if FreeCAD.GuiUp:
        import FreeCADGui as FGui
        from PySide import QtCore, QtGui
        util.GUI = True
        GUI = True


frontend = None
if not check_dependencies():
    raise ImportError

from programmaticInterface import *
