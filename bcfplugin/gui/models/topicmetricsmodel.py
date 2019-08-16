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
This file provides the TopicMetricsModel. It provides the the metrics table
inside the topic metrics dialog with its data to display. Where the data is
just for each row a member name and member value pair of an instance of Topic
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

logger = bcfplugin.createLogger(__name__)


class TopicMetricsModel(QAbstractTableModel):

    """ Model for the table that shows metrics of the topic.

    The uuid will not be visible in the metrics view. """


    def __init__(self, parent = None):

        QAbstractTableModel.__init__(self, parent)
        self.disabledIndices = [ 1, 2, 7, 8 ]
        """ Indices of items that cannot be edited and shall be disabled. """
        self.topic = None
        """ Currently open topic """
        self.members = []
        """ List of all names of members of a topic that shall be displayed.
        """


    def data(self, index, role = Qt.DisplayRole):

        """ Returns the value for a member topic specified by `index`. """

        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        member = self.members[index.row()]
        if index.column() == 0:
            return member.xmlName
        elif index.column() == 1:
            return str(member.value)
        else:
            # I don't know what an additional column could display actually
            return None


    def headerData(self, section, orientation, role = Qt.DisplayRole):

        """ Returns the data that shall be displayed in the horiz. header row.
        """

        header = None
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                header = "Property"
            elif section == 1:
                header = "Value"

        return header


    def flags(self, index):

        """ Items, if not in the disabled list, can be edited and selected. """

        flags = Qt.NoItemFlags
        if not index.isValid():
            return flags
        # every disabled row just shall be greyed out, but its content still
        # visible
        if index.column() == 0:
            flags |= Qt.ItemIsSelectable
            flags |= Qt.ItemIsEnabled

        if index.column() == 1:
            flags = Qt.ItemIsSelectable
            flags |= Qt.ItemIsEditable
            flags |= Qt.ItemIsEnabled

        if index.column() == 1 and index.row() in self.disabledIndices:
            flags = Qt.NoItemFlags

        return flags


    def setData(self, index, value, role = Qt.EditRole):

        """ Update a member of topic with the value entered by the user """

        if not index.isValid():
            return False

        try:
            self.members[index.row()].value = value[0]
        except Exception as err:
            logger.error(str(err))
            return False

        result = pI.modifyElement(self.topic, value[1])
        if result == pI.OperationResults.FAILURE:
            return False

        topic = pI.getTopic(self.topic)
        self.resetItems(topic)
        return True


    def rowCount(self, parent = QModelIndex()):

        """ Returns the number of properties the view shall display.

        There are exactly only 12 members whose values can be displayed in the
        property value tableview. """

        return 12


    def columnCount(self, parent = QModelIndex()):

        """ Returns the number of columns to be displayed in the tableview.

        Only two columns will be shown. The first contains the name of the
        value, the second one the value itself.
        """

        return 2


    @Slot(Topic)
    def resetItems(self, topic = None):

        """ Resets the internal state of the model to the new topic, or its
        initial state. """

        self.beginResetModel()

        if topic is None:
            self.topic = None
            self.members = []
        else:
            self.topic = topic
            self.members = self.createMembersList(self.topic)

        self.endResetModel()


    def createMembersList(self, topic):

        """ Create and return an ordered list of members, in the order they
        shall be shown.

        An object inside this list will be the underlying object representing
        the value. This is done to be able to access the xmlName which is used
        as the name of the value.
        """

        members = [topic._title, topic._date, topic._author, topic._type,
                topic._status, topic._priority, topic._index, topic._modDate,
                topic._modAuthor, topic._dueDate, topic._assignee,
                topic._description ]

        return members


