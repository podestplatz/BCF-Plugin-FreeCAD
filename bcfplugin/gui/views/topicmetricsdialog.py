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

import os
import sys
import logging
import platform
import pyperclip
import subprocess

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import (QAbstractListModel, QModelIndex, Slot, Signal,
        QDir, QPoint, QSize, QTimer)

import bcfplugin
from bcfplugin.gui.views import (openAuthorsDialog, createNotificationLabel,
        showNotification)

logger = bcfplugin.createLogger(__name__)


class TopicMetricsDialog(QDialog):

    """ Dialog showing details to a topic.

    Details include:
        - all simple xml nodes contained in the topic node, shown as
          Property:Value table
        - a list of additional documents, specified in the topic node
        - a list of related topics, specified in the topic node
    """

    def __init__(self, parent = None):

        QDialog.__init__(self, parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # setup table for simple xml nodes.
        self.topicMetrics = QTableView()
        self.topicMetrics.setModel(parent.topicDetailsModel)
        self.setMinVertTableSize(self.topicMetrics)
        self.topicMetrics.setItemDelegate(parent.topicDetailsDelegate)
        self.layout.addWidget(self.topicMetrics)

        # setup list showing additional documents
        self.addDocGroup = QGroupBox()
        self.addDocGroup.setTitle(self.addDocGroup.tr("Additional Documents"))
        self.addDocGroupLayout = QVBoxLayout(self.addDocGroup)
        self.addDocTable = QTableView()
        self.addDocTable.setModel(parent.addDocumentsModel)
        self.setMinVertTableSize(self.addDocTable)
        self.addDocTable.doubleClicked.connect(self.openDocRef)
        self.addDocTable.pressed.connect(self.showDoubleClickHint)
        self.addDocGroupLayout.addWidget(self.addDocTable)
        if parent.addDocumentsModel.rowCount() == 0:
            self.addDocTable.hide()
        self.layout.addWidget(self.addDocGroup)

        # setup list showing related topics.
        self.relTopGroup = QGroupBox()
        self.relTopGroup.setTitle(self.relTopGroup.tr("Related Topics"))
        self.relTopGroupLayout = QVBoxLayout(self.relTopGroup)
        self.relTopList = QListView()
        self.relTopList.setModel(parent.relTopModel)
        self.relTopGroupLayout.addWidget(self.relTopList)
        if parent.relTopModel.rowCount() == 0:
            self.relTopList.hide()
        self.layout.addWidget(self.relTopGroup)

        self.notificationLabel = createNotificationLabel()
        # add it to the main windows members because it is accessed in
        # openDocRef()
        self.layout.addWidget(self.notificationLabel)


    @Slot()
    def openDocRef(self, index):

        """ Opens an additional document specified by `index` or copies the path
        to clipboard.

        The behavior is determined by the column, in which the double clicked
        element resides. For elements in the first column it is tried to open
        them with the default application of the platform.
        For elements in the second column the content is copied to the
        clipboard.
        """

        filePath = index.model().getFilePath(index)
        if index.column() == 0:
            if not os.path.exists(filePath):
                showNotification(self, "File does not exist locally. Cannot"\
                        " be opened")
                return
            if filePath is not None:
                system = platform.system()
                if system == "Darwin": # this my dear friend is macOS
                    subprocess.call(["open", filePath])
                elif system == "Windows": # ... well, MS Windows
                    os.startfile(filePath)
                else: # good old linux derivatives
                    subprocess.call(["xdg-open", filePath])
        else: # copy path to clipboard and notify the user about it
            pyperclip.copy(index.model().data(index))
            showNotification(self, "Copied path to clipboard.")


    @Slot(QModelIndex)
    def showDoubleClickHint(self, index):

        """ Shows a notification, informing about the double click behavior. """

        filePath = index.model().getFilePath(index)
        if index.column() == 0:
            if os.path.exists(filePath):
                showNotification(self, "Double click to open document.")
        elif index.column() == 1:
            showNotification(self, "Double click to copy path.")


    def setMinVertTableSize(self, table):

        """ This function calculates the minimum vertical size the table needs
        to display its contents without a scrollbar and sets it.

        This function assumes that it is called after the model is set.
        This code was adapted from:
        https://stackoverflow.com/questions/42458735/how-do-i-adjust-a-qtableview-height-according-to-contents
        """

        totalHeight = 0
        for i in range(0, table.verticalHeader().count()):
            if not table.verticalHeader().isSectionHidden(i):
                totalHeight += table.verticalHeader().sectionSize(i)

        if not table.horizontalScrollBar().isHidden():
            totalHeight += table.horizontalScrollBar().height()

        if not table.horizontalHeader().isHidden():
            totalHeight += table.horizontalHeader().height()

        logger.info("Setting size of AddDocTable to {}".format(totalHeight))
        table.setMinimumHeight(totalHeight)



