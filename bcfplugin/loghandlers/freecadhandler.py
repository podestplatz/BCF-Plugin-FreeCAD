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
This file provides a logging handler for the logging framework of python. Its
purpose is to write the five different kinds of logging messages to their
appropriate counterparts in FreeCAD's Console framework.
Following the mapping is depicted:
            _____
 Message Type/|\FreeCAD Console Sink
-------------|||---------------------
 Debug       \|/PrintLog
 Info         | PrintMessage
 Warning      | PrintWarning
 Error        | PrintError
 Critical     | PrintError
"""

import logging
from logging import Handler

import FreeCAD as App


class FreeCADHandler(Handler):

    def __init__(self, level=logging.NOTSET):
        Handler.__init__(self, level)


    def emit(self, record):

        console = App.Console
        msg = self.format(record) + "\n"
        level = record.levelno
        if level == logging.DEBUG:
            console.PrintLog(msg)
        elif level == logging.INFO:
            console.PrintMessage(msg)
        elif level == logging.WARNING:
            console.PrintWarning(msg)
        elif (level == logging.ERROR or
                level == logging.CRITICAL):
            console.PrintError(msg)
        else:
            # I don't know what to do
            pass

