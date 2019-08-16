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

"""
Author: Patrick Podest
Date: 2019-08-16
Github: @podestplatz

**** Description ****
This file initializes the plugin global variables and imports everything from
the programmaticInterface into the plugin global namespace. It further is
responsible for checking whether all dependency requirements are met by the
system.
It further initializes the logging system of python and provides
`createLogger()` which is intended to be called by every submodule to attain a
separate instance of logging.Logger.
"""

import os
import sys
import logging
import importlib
from enum import Enum

import bcfplugin.util as util
from bcfplugin.loghandlers.freecadhandler import FreeCADHandler
from bcfplugin.loghandlers.stdoutfilter import StdoutFilter

excPath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, excPath)

__all__ = ["programmaticInterface", "ui"]

FREECAD = False
""" Set by BCFPlugin.py when running inside FreeCAD """

GUI = False
""" Set by BCFPlugin.py when running in Gui mode """

dependencies = ["dateutil", "pytz", "pyperclip", "xmlschema"]
""" Packages this plugin depends on. """

LOGFORMAT = "[%(levelname)s]%(module)s.%(funcName)s(): %(message)s"
""" Format of all logged messages """

PREFIX = "bcfplugin_"

LOGFILE = "{}log.txt".format(PREFIX)


def printErr(msg):

    """ Print an error using FreeCAD.Console or stderr. """

    global FREECAD

    if FREECAD:
        FreeCAD.Console.PrintError(msg)
    else:
        print(msg, file=sys.stderr)


def printInfo(msg):

    """ Print an informational message using FreeCAD.Console or stdout. """

    global FREECAD

    if FREECAD:
        FreeCAD.Console.PrintMessage(msg)
    else:
        print(msg)


def getFreeCADHandler():

    """ Create and return an instance of the FreeCAD logging handler.

    This handler uses FreeCAD's Console system to print messages of the 5
    different severity levels to the user.
    """

    handler = FreeCADHandler()
    handler.setLevel(logging.DEBUG)

    filter = StdoutFilter()
    format = logging.Formatter(LOGFORMAT)
    handler.setFormatter(format)
    handler.addFilter(filter)

    return handler


def getStdoutHandler():

    """ Returns a handler for the logging facility of python, writing the
    messages to stdout """

    handler = logging.StreamHandler(stream = sys.stdout)
    handler.setLevel(logging.DEBUG)

    filter = StdoutFilter()
    format = logging.Formatter(LOGFORMAT)
    handler.setFormatter(format)
    handler.addFilter(filter)

    return handler


def getFileHandler(fpath):

    """ Returns a handler for the logging facility of python, writing the
    messages to file `fpath` """

    handler = logging.FileHandler(fpath)
    handler.setLevel(logging.DEBUG)

    format = logging.Formatter(LOGFORMAT)
    handler.setFormatter(format)

    return handler


def createLogger(name):

    """ Creates a new logger instance with module name = `name`.

    The new instance is then returned.
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    return logger


def check_dependencies():

    """ Checks whether all modules listed in `dependencies` are available.

    To check, it is tried to import every module. If one fails an error message
    will be printed in addition to an informational message about how to
    install a missing dependency.
    """

    available = True

    for dependency in dependencies:
        try:
            importlib.import_module(dependency)
        except Exception as e:
            pkg = dependency
            available = False
            break

    if not available:
        printError("Could not find the module `{}`. Install it through"\
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

# delete temporary artifacts
import util
util.deleteTmp()

# create working directory
path = util.getSystemTmp()
logfile = os.path.join(path, LOGFILE)

# generate config for root logger
logHandlers = [getFileHandler(logfile)]
if FREECAD:
    logHandlers.append(getFreeCADHandler())
else:
    logHandlers.append(getStdoutHandler())
logging.basicConfig(level=logging.INFO, handlers=logHandlers)

# for nonGUI-mode import __all__ of pI into this namespace
from programmaticInterface import *
