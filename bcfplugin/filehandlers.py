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
