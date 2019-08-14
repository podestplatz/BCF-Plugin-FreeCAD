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
from PySide2.QtWidgets import QListView, QLabel, QPushButton
from PySide2.QtCore import Signal, QSize, Slot, QModelIndex
from PySide2.QtGui import *

import bcfplugin
from bcfplugin.rdwr.viewpoint import Viewpoint

logger = bcfplugin.createLogger(__name__)


class ViewpointsView(QListView):

    """ Ordinary ListView, adding hooks to activate a viewpoint in the object
    view of FreeCAD. """


    def __init__(self, parent = None):

        QListView.__init__(self, parent)


    @Slot(Viewpoint)
    def selectViewpoint(self, viewpoint: Viewpoint):

        """ Selects the `viewpoint` in the list. """

        start = self.model().createIndex(0, 0)
        searchValue = str(viewpoint.file) + " (" + str(viewpoint.id) + ")"
        matches = self.model().match(start, Qt.DisplayRole, searchValue)
        if len(matches) > 0:
            self.setCurrentIndex(matches[0])


    @Slot(QModelIndex, QPushButton)
    def activateViewpoint(self, index, rstBtn):

        """ Activates the viewpoint given by `index` in FreeCAD's object view.
        """

        result = self.model().activateViewpoint(index)
        if result:
            rstBtn.show()


    def findViewpoint(self, desired: Viewpoint):

        """ Searches for the `desired` viewpoint in the model.

        Returns the indes in the model if found, otherwise -1 is returned.
        """

        index = -1
        for i in range(0, self.model().rowCount()):
            index = self.model().createIndex(i, 0)
            data = self.model().data(index, Qt.DisplayRole)

            if str(desired.id) in data:
                index = i
                break

        return index



