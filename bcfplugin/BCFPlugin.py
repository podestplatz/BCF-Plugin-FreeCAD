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
BCFPlugin.py is responsible for initializing the plugin in both modes: GUI and
non-GUI mode. The plugin assumes that it is running in FreeCAD.

The main function, and entry point into this file, is `start()`.
"""

import sys
import bcfplugin.util as util
from bcfplugin import FREECAD, GUI


def setup_gui():

    """ Starts the Qt part of the plugin. """

    import bcfplugin.gui.plugin_panel as panel
    qtWindow = panel.launch_ui()
    return qtWindow


def setup_nonGui():
    help_str = """
This module lets you to operate on BCF files. Therefore multiple modules
can be imported:
    - bcf.reader: lets you read in the desired BCF file. Most important function
      here is: bcf.reader.readBcfFile(absolutePathToFile: str) -> Project
      The returned object is of greatest importance since you want to operate on
      it.
    - bcf.writer: lets you write out the contents of an object of type `Project`
      to the desired path. Most important function is:
      bcf.writer.addUpdate(project: Project, element, prevVal)

"""
    if not check_dependencies():
        return

    import frontend.programmaticInterface as plugin

    project = plugin.openProject("./bcf/test_data/Issues_BIMcollab_Example.bcf.original")
    topics = plugin.getTopics()
    a = lambda x: x[1].index
    util.printInfo([ a(topic) for topic in topics ])

    viewpoints = plugin.getViewpoints(topics[0][1])
    util.printInfo(viewpoints)

    comments = plugin.getComments(topics[0][1], viewpoints[0][1])
    util.printInfo(comments)

    files = list()
    for (topicUUID, topic) in topics:
        files.append(plugin.getRelevantIfcFiles(topic))
    util.printInfo(files)


def start():

    """ Starts the plugin either in gui or non-gui mode """

    sys.path.append("../")

    if GUI:
        return setup_gui()
    else:
        return setup_nonGui()


"""
If run in the command line a little help shall be printed on what the user is
able to do and how.
"""
if __name__ == "__main__":
    setup()

