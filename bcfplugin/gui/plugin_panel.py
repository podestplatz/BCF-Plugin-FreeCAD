import bcfplugin.util as util
from bcfplugin.gui import plugin_view as view

from PySide2.QtWidgets import QDialogButtonBox, QWidget, QPushButton, QApplication
import FreeCADGui
import FreeCAD


def launch_ui():

    """ Adds the plugin view as Dialog window to FreeCAD """

    panel = BCFPluginPanel()
    FreeCADGui.Control.showDialog(panel)


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

        self.form.closeEvent(None)


    def reject(self):

        """ Called when the 'Close' button of the task dialog is pressed,
        closes the panel and returns nothing """

        util.printInfo("Closing the dialog")

        FreeCADGui.Control.closeDialog()
        if FreeCAD.ActiveDocument:
            FreeCAD.ActiveDocument.recompute()
