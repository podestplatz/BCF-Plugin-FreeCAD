from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import (QAbstractListModel, QModelIndex, Slot, Signal,
        QDir, QPoint, QSize, QTimer)

import bcfplugin
import bcfplugin.util as util
import bcfplugin.gui.plugin_delegate as delegate
import bcfplugin.gui.plugin_view as view
import bcfplugin.gui.plugin_model as model
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
