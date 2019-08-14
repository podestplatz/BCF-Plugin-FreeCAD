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

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import (QAbstractListModel, QModelIndex, Slot, Signal,
        QDir, QPoint, QSize, QTimer)

import bcfplugin
import bcfplugin.util as util
import bcfplugin.gui.views as view
import bcfplugin.gui.models as model
from bcfplugin.rdwr.topic import Topic

logger = bcfplugin.createLogger(__name__)


class ProjectCreateDialog(QDialog):

    def __init__(self, parent = None):

        QDialog.__init__(self, parent)

        mainLayout = QVBoxLayout(self)
        formLayout = QFormLayout()

        self.nameEdit = QLineEdit()
        self.nameEdit.setObjectName("Project Name")

        #extSchemaUriEdit = QLineEdit()
        #extSchemaUriEdit.setObjectName("Extension Schema Uri")

        submitBtn = QPushButton(self.tr("Submit"))
        submitBtn.clicked.connect(self.createProject)

        self.notificationLabel = view.createNotificationLabel()

        formLayout.addRow("Project Name", self.nameEdit)
        #formLayout.addRow("Extension Schema Uri", extSchemaUriEdit)

        mainLayout.addLayout(formLayout)
        mainLayout.addWidget(submitBtn)
        mainLayout.addWidget(self.notificationLabel)


    def createProject(self):

        name = self.nameEdit.text()
        extSchema = "" #extSchemaUriEdit()
        if not model.createProject(name, extSchema):
            view.showNotification(self, "Project could not be created.")
        else:
            self.done(0)
