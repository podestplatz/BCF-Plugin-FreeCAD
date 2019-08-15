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
from copy import copy

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import (QModelIndex, Slot, QSize, QPoint, Signal, Qt, QRect)

import bcfplugin
import bcfplugin.util as util
from bcfplugin.gui.views import openAuthorsDialog


logger = bcfplugin.createLogger(__name__)

dueDateRegex = "\d{4}-[01]\d-[0-3]\d"


class TopicMetricsDelegate(QStyledItemDelegate):

    """
    This delegate class is used for controlling the data entry of in the topic
    metrics window.

    It also, like the comment delegate, checks whether the user already has
    entered his/her email address that will be set inserted ModifiedAuthor in
    the data model.
    """

    def __init__(self, parent = None):

        QStyledItemDelegate.__init__(self, parent)


    def createEditor(self, parent, option, index):

        """ Creates an QLineEdit object and returns it as editor to the view.

        The QLineEdit is supplied with a validator object if the editor shall
        be created for dueDate field.
        """

        modAuthor = ""
        if util.isAuthorSet():
            modAuthor = util.getAuthor()
        else:
            openAuthorsDialog(None)
            modAuthor = util.getAuthor()

        logger.debug("The email you entered is: {}".format(modAuthor))

        model = index.model()
        dueDateIndex = model.members.index(model.topic._dueDate)

        startValue = "" # TODO: use current value
        editor = QLineEdit(startValue, parent)
        if index.row() == dueDateIndex:
            validator = QRegExpValidator()
            validator.setRegExp(dueDateRegex)

            editor.setValidator(validator)
            editor.setFrame(True)
        return editor


    def setModelData(self, editor, model, index):

        """ Updates the model at `index` with the current text of the editor """

        text = editor.text()
        value = (text, util.getAuthor())
        success = model.setData(index, value)
        if not success:
            logger.error("The value could not be updated.")
