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
from PySide2.QtCore import (QModelIndex, Slot, QSize, QPoint, Signal, Qt, QRect)

import bcfplugin
import bcfplugin.util as util
from bcfplugin.gui.regex import emailRegex


author = ""
""" Holds the entered email address of the author """

authorsDialog = None
authorsLineEdit = None
@Slot()
def setAuthor():

    global authorsDialog
    global authorsLineEdit

    author = authorsLineEdit.text()
    authorsDialog.author = author
    authorsDialog.done(0)


def openAuthorsDialog(parent):

    global authorsDialog
    global authorsLineEdit

    authorsDialog = QDialog(parent)
    authorsDialog.setWindowTitle("Enter your e-Mail")

    form = QFormLayout()
    emailValidator = QRegExpValidator()
    emailValidator.setRegExp(emailRegex)

    authorsLineEdit = QLineEdit(parent)
    authorsLineEdit.setValidator(emailValidator)
    authorsLineEdit.editingFinished.connect(setAuthor)

    form.addRow("E-Mail:", authorsLineEdit)
    authorsDialog.setLayout(form)
    authorsDialog.exec()

    author = authorsDialog.author
    util.setAuthor(author)


