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

import logging

import FreeCADGui
import FreeCAD
from PySide2.QtWidgets import QDialogButtonBox, QWidget, QPushButton, QApplication

import bcfplugin
import bcfplugin.util as util
from bcfplugin.gui import plugin_view as view

logger = bcfplugin.createLogger(__name__)


def launch_ui():

    """ Adds the plugin view as Dialog window to FreeCAD """

    panel = BCFPluginPanel()
    FreeCADGui.Control.showDialog(panel)

    return panel


class BCFPluginPanel:

    """ Instantiates the panel that will be shown as dialog in FreeCAD.

    Also this class adds a Save and Close action to the file menu.
    """

    def __init__(self):

        self.running = True
        self.form = view.MyMainWindow()
        self.form.resize(self.form.geometry().width(), self.form.geometry().height())
        self.form.setObjectName("BCFPlugin")


    def getMainWindow():

        """ Retrieves the global main window reference from Qt. """

        mainWindow = None
        topLvl = QApplication.topLevelWidgets()
        for widget in topLvl:
            if widget.metaObject().className() == "Gui::MainWindow":
                mainWindow = widget
                break

        if mainWindow is None:
            raise RuntimeError("No main window found!")

        return mainWindow


    def needsFullSpace(self):

        """ Notify FreeCAD that the full space is needed for the panel """

        return True


    def clicked(self, qButton):

        """ Called when the open button is pressed in the button row above the
        panel """

        if (qButton == QDialogButtonBox.Open):
            self.form.projectButton.clicked.emit()
        elif (qButton == QDialogButtonBox.Close):
            self.close()


    def getStandardButtons(self):

        """ Show the close and a open button be visible in the row above the panel """

        return int(QDialogButtonBox.Close)


    def close(self):

        """ Calls the plugins closeEvent function. """

        self.form.closeEvent(None)


    def reject(self):

        """ Called when the 'Close' button of the task dialog is pressed,
        closes the panel and returns nothing """

        logger.info("Closing the dialog")

        FreeCADGui.Control.closeDialog()
        if FreeCAD.ActiveDocument:
            FreeCAD.ActiveDocument.recompute()
