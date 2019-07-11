from bcfplugin.gui import plugin_view as view

from PySide2.QtWidgets import QDialogButtonBox
import FreeCADGui
import FreeCAD


def launch_ui():

    """ Adds the plugin view as Dialog window to FreeCAD """

    FreeCADGui.Control.showDialog(BCFPluginPanel())


class BCFPluginPanel:

    """ Instantiates the panel that will be shown as dialog in FreeCAD.

    Also this class adds a Save and Close action to the file menu.
    """

    def __init__(self):

        self.running = True
        self.form = view.MyMainWindow()


    def needsFullSpace(self):

        """ Notify FreeCAD that the full space is needed for the panel """

        return True


    def getStandardButtons(self):

        """ Let only the close button be visible in the row above the panel """

        return int(QDialogButtonBox.Close)


    def reject(self):

        """ Called when the 'Close' button of the task dialog is pressed,
        closes the panel and returns nothing """

        FreeCADGui.Control.closeDialog()
        if FreeCAD.ActiveDocument:
            FreeCAD.ActiveDocument.recompute()
