import bcfplugin
import bcfplugin.BCFPlugin as plugin
import bcfplugin.gui.plugin_model as model
import bcfplugin.gui.plugin_view as view


def open(file):

    """ Starts the UI and already loads the `file`.

    This function is called by FreeCAD as handler for *.bcf and *.bcfzip files,
    when such shall be opened.
    """

    import FreeCAD as App
    try:
        import FreeCADGui as Gui

        qtWindow = Gui.getMainWindow().findChild(view.OBJECTNAME)
        if qtWindow is None:
            panel = plugin.start()
            qtWindow = panel.form

        model.openProjectBtnHandler(file)
        qtWindow.openFilePath = file
        qtWindow.projectOpened.emit()

    except:
        bcfplugin.openProject(file)

        return



def insert(file, doc):

    """ Wrapper for `open()`. """

    open(file)
