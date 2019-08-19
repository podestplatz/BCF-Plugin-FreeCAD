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
This file provides the topic add dialog. It is responsible for gathering the
necessary data to add a topic to the currently open project.
"""

import datetime
from uuid import uuid4

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import bcfplugin
import bcfplugin.util as util
import bcfplugin.gui.views as view
import bcfplugin.gui.models as model
from bcfplugin.gui.regex import dueDateRegex, emailRegex
from bcfplugin.rdwr.topic import Topic

logger = bcfplugin.createLogger(__name__)


class TopicAddDialog(QDialog):

    titleRegex = "^[a-zA-Z0-9]+$"
    descRegex = "^[ a-zA-Z0-9]*$"
    typeRegex = descRegex
    statusRegex = descRegex
    prioRegex = descRegex
    idxRegex = "^[0-9]*$"
    lblRegex = "^[a-zA-Z0-9]*(,\s?[a-zA-Z0-9]+)*$"
    dueDateRegex = dueDateRegex
    assigneeRegex = emailRegex
    stageRegex = descRegex


    def __init__(self, parent = None):

        QDialog.__init__(self, parent)
        self.setWindowTitle("Add Topic")

        mainLayout = QVBoxLayout()
        formLayout = QFormLayout()
        btnLayout = QHBoxLayout()
        self.setLayout(mainLayout)

        self.createValidators()
        self.createEditFields()
        self.setupLayout(formLayout)

        self.submitBtn = QPushButton("Submit")
        self.submitBtn.pressed.connect(self.createTopic)
        btnLayout.addStretch()
        btnLayout.addWidget(self.submitBtn)

        self.notificationLabel = view.createNotificationLabel()

        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(btnLayout)
        mainLayout.addWidget(self.notificationLabel)


    def setupLayout(self, formLayout):

        formLayout.addRow(self.tr("Title (*)"), self.titleEdit)
        formLayout.addRow(self.tr("Description"), self.descEdit)
        formLayout.addRow(self.tr("Type"), self.typeEdit)
        formLayout.addRow(self.tr("Status"), self.statusEdit)
        formLayout.addRow(self.tr("Priority"), self.prioEdit)
        formLayout.addRow(self.tr("Index (default -1)"), self.idxEdit)
        formLayout.addRow(self.tr("Labels (comma separated)"), self.lblEdit)
        formLayout.addRow(self.tr("Due date"), self.dueDateEdit)
        formLayout.addRow(self.tr("Assign to"), self.assigneeEdit)
        formLayout.addRow(self.tr("Stage"), self.stageEdit)


    def createEditFields(self):

        todayDateStr = datetime.datetime.now().strftime("%Y-%m-%d")

        self.titleEdit = QLineEdit()
        self.titleEdit.setValidator(self.titleValidator)
        self.titleEdit.setObjectName("Title")
        self.typeEdit = QLineEdit()
        self.typeEdit.setValidator(self.typeValidator)
        self.typeEdit.setObjectName("Type")
        self.statusEdit = QLineEdit()
        self.statusEdit.setValidator(self.statusValidator)
        self.statusEdit.setObjectName("Status")
        self.prioEdit = QLineEdit()
        self.prioEdit.setValidator(self.prioValidator)
        self.prioEdit.setObjectName("Priority")
        self.idxEdit = QLineEdit()
        self.idxEdit.setValidator(self.idxValidator)
        self.idxEdit.setObjectName("Index")
        self.idxEdit.setPlaceholderText("Enter a number")
        self.lblEdit = QLineEdit()
        self.lblEdit.setValidator(self.lblValidator)
        self.lblEdit.setObjectName("Labels")
        self.lblEdit.setPlaceholderText("Comma separated list")
        self.dueDateEdit = QLineEdit()
        self.dueDateEdit.setValidator(self.dueDateValidator)
        self.dueDateEdit.setObjectName("DueDate")
        self.dueDateEdit.setPlaceholderText(todayDateStr)
        self.assigneeEdit = QLineEdit()
        self.assigneeEdit.setValidator(self.assigneeValidator)
        self.assigneeEdit.setObjectName("Assignee")
        self.assigneeEdit.setPlaceholderText("tim@example.org")
        self.descEdit = QLineEdit()
        self.descEdit.setValidator(self.descValidator)
        self.descEdit.setObjectName("Description")
        self.stageEdit = QLineEdit()
        self.stageEdit.setValidator(self.stageValidator)
        self.stageEdit.setObjectName("Stage")

        self.editFields = [ self.titleEdit, self.typeEdit, self.statusEdit,
                self.prioEdit, self.idxEdit, self.lblEdit, self.dueDateEdit,
                self.assigneeEdit, self.descEdit, self.stageEdit ]


    def createValidators(self):

        self.titleValidator = QRegExpValidator()
        self.titleValidator.setRegExp(self.titleRegex)
        self.descValidator = QRegExpValidator()
        self.descValidator.setRegExp(self.descRegex)
        self.typeValidator = QRegExpValidator()
        self.typeValidator.setRegExp(self.typeRegex)
        self.statusValidator = QRegExpValidator()
        self.statusValidator.setRegExp(self.statusRegex)
        self.prioValidator = QRegExpValidator()
        self.prioValidator.setRegExp(self.prioRegex)
        self.idxValidator = QRegExpValidator()
        self.idxValidator.setRegExp(self.idxRegex)
        self.lblValidator = QRegExpValidator()
        self.lblValidator.setRegExp(self.lblRegex)
        self.dueDateValidator = QRegExpValidator()
        self.dueDateValidator.setRegExp(self.dueDateRegex)
        self.assigneeValidator = QRegExpValidator()
        self.assigneeValidator.setRegExp(self.assigneeRegex)
        self.stageValidator = QRegExpValidator()
        self.stageValidator.setRegExp(self.stageRegex)


    @Slot()
    def createTopic(self):

        if not self.checkInput():
            return

        if not util.isAuthorSet():
            view.openAuthorsDialog(None)
        creationAuthor = util.getAuthor()

        dueDate = None
        if self.dueDateEdit.text() != "":
            dueDate = datetime.datetime.fromisoformat(self.dueDateEdit.text())

        labels = []
        if self.lblEdit.text() != "":
            labels = [ label.strip() for label in self.lblEdit.text().split(',') ]

        idx = self.idxEdit.text()

        newTopic = { "title": self.titleEdit.text(),
                "author": creationAuthor,
                "type": self.typeEdit.text(),
                "status": self.statusEdit.text(),
                "referenceLinks": [], # referenceLinks
                "description": self.descEdit.text(),
                "priority": self.prioEdit.text(),
                "index": int(idx) if idx != "" else -1,
                "labels": labels,
                "dueDate": dueDate,
                "assignee": self.assigneeEdit.text(),
                "stage": self.stageEdit.text() }

        if not model.addTopic(newTopic):
            logger.error("Could not add topic {}".format(newTopic))
            view.showNotification("Addition of the topic was unsuccessful.")
        else:
            logger.info("New topic added!")
            self.done(0)


    def checkInput(self):

        allValid = True
        invalidField = None

        for field in self.editFields:
            text = field.text()
            validator = field.validator()

            # dueDate may be empty
            if text == "" and field == self.dueDateEdit:
                continue

            result = validator.validate(text, 0)
            if (result[0] == QValidator.State.Invalid or
                    result[0] == QValidator.State.Intermediate):
                allValid = False
                invalidField = field
                break

        if not allValid:
            view.showNotification(self, "Text of field {} is"\
                    " invalid".format(invalidField.objectName()))
            return False

        if self.dueDateEdit.text() != "":
            try:
                datetime.datetime.fromisoformat(self.dueDateEdit.text())
            except ValueError as err:
                view.showNotification(self, "DueDate: {}".format(str(err)))
                return False

        return True
