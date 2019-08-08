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

