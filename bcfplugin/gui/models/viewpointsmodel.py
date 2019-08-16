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
This file provides the ViewpointsModel class, which provides the ViewpointsView
with data to display.
"""

import os
import copy
import logging
from uuid import uuid4

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import (QAbstractListModel, QAbstractTableModel,
        QModelIndex, Slot, Signal, Qt, QSize)

import bcfplugin
import bcfplugin.programmaticInterface as pI
import bcfplugin.util as util
from bcfplugin.rdwr.topic import Topic
from bcfplugin.rdwr.markup import Comment
from bcfplugin.frontend.viewController import CamType

logger = bcfplugin.createLogger(__name__)


class ViewpointsListModel(QAbstractListModel):

    """
    Model class to the viewpoins list.

    It returns the name of a viewpoint, associated with the current topic as
    well as an icon of the snapshot file that is referenced in the viewpoint. If
    no snapshot is referenced then no icon is returned.  An icon is 10x10
    millimeters in dimension. The actual sizes and offsets, in pixels, are
    stored in variables containing 'Q'. All other sizes and offset variables
    hold values in millimeters.These sizes and offsets are scaled to the
    currently active screen, retrieved by `util.getCurrentQScreen()`.
    """

    def __init__(self, snapshotModel, parent = None):

        QAbstractListModel.__init__(self, parent = None)
        self.viewpoints = []
        """ List of instances of `ViewpointReference` """
        # used to retrieve the snapshot icons.
        self.snapshotModel = snapshotModel
        """ Reference to SnapshotModel used to retrieve icons of the snapshots
        """

        # set up the sizes and offsets
        self._iconQSize = None
        """ Size in pixels """
        self._iconSize = QSize(10, 10)
        """ Size in millimeters """
        self.calcSizes()


    def data(self, index, role = Qt.DisplayRole):

        """ Returns the file name and an icon of the snapshot associated to a
        viewpoint. """

        if not index.isValid():
            return None

        viewpoint = self.viewpoints[index.row()]
        if role == Qt.DisplayRole:
            # return the name of the viewpoints file
            return str(viewpoint.file) + " (" + str(viewpoint.id) + ")"

        elif role == Qt.DecorationRole:
            # if a snapshot is linked, return an icon of it.
            filename = str(viewpoint.snapshot)
            icon = self.snapshotModel.imgFromFilename(filename)
            if icon is None: # snapshot is not listed in markup and cannot be loaded
                return None

            scaledIcon = icon.scaled(self._iconQSize, Qt.KeepAspectRatio)
            return scaledIcon


    def rowCount(self, parent = QModelIndex()):

        """ Returns the amount of viewpoints that shall be listed in the view
        """

        return len(self.viewpoints)


    @Slot()
    def resetItems(self, topic = None):

        """ If `topic != None` load viewpoints associated with `topic`, else
        delete the internal state of the model """

        self.beginResetModel()

        if topic is None:
            self.viewpoints = []
        else:
            self.viewpoints = [ vp[1] for vp in pI.getViewpoints(topic, False) ]

        self.endResetModel()


    @Slot()
    def resetView(self):

        """ Reset the view of FreeCAD to the state before the first viewpoint
        was applied """

        pI.resetView()


    @Slot()
    def calcSizes(self):

        """ Convert the millimeter sizes/offsets into pixels depending on the
        current screen. """

        screen = util.getCurrentQScreen()
        # pixels per millimeter (not parts per million)
        ppm = screen.logicalDotsPerInch() / util.MMPI

        width = self._iconSize.width() * ppm
        height = self._iconSize.height() * ppm
        self._iconQSize = QSize(width, height)


    @Slot(QModelIndex)
    def activateViewpoint(self, index):

        """ Manipulates FreeCAD's object viewer according to the setting of the
        viewpoint. """

        if not index.isValid() or index.row() >= len(self.viewpoints):
            return False

        vpRef = self.viewpoints[index.row()]
        camType = None
        if vpRef.viewpoint.oCamera is not None:
            camType = CamType.ORTHOGONAL
        elif vpRef.viewpoint.pCamera is not None:
            camType = CamType.PERSPECTIVE

        result = pI.activateViewpoint(vpRef.viewpoint, camType)
        if result == pI.OperationResults.FAILURE:
            return False
        return True


    def setIconSize(self, size: QSize):

        """ Size is expected to be given in millimeters. """

        self._iconSize = size
        self.calcSizes()
