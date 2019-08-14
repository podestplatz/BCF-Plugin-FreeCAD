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


