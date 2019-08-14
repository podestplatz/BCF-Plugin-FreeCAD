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


class CommentDelegate(QStyledItemDelegate):


    def __init__(self, parent = None):

        QStyledItemDelegate.__init__(self, parent)
        self.baseFontSize = 12
        self.commentFont = QFont("times")
        self.updateFonts(self.commentFont)
        self.widgetWidth = 0

        self._commentYOffset = 2
        self._commentYQOffset = None
        self._commentXOffset = 2
        self._commentXQOffset = None
        self._separationLineThickness = 0.5
        self._separationLineQThickness = None
        self._verticalOffset = 1
        self._verticalQOffset = None
        self._authorDateSeparation = 1
        self._authorDateQSeparation = None
        self._maxCommentHeight = None
        self.computeSizes()

        # storage of the size hints. used to intelligently emit the
        # sizeHintChanged signal
        self.sizeHints = {}


    def paint(self, painter, option, index):

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        idx = index.row()

        comment = index.model().data(index, Qt.DisplayRole)
        # top y coordinate at which drawing will begin downwards
        leftX = option.rect.x()
        topY = option.rect.y()

        # save painter state, since color and font are changed
        painter.save()

        # whole area that can be drawn onto
        boundingRect = painter.viewport()

        # extract pen and font from painter
        pen = painter.pen()
        self.updateFonts(painter.font())
        fontMetric = painter.fontMetrics()

        # draw comment
        brush = index.model().data(index, Qt.ForegroundRole)
        (commentStart, commentTextHeight) = self.drawComment(comment,
                painter, option, fontMetric, leftX, topY, brush)

        # draw separation line
        lineStart = QPoint(commentStart.x(),
                commentStart.y())
        self.drawSeparationLine(painter, pen, lineStart, self.width - 20)

        # draw author
        authorStart = QPoint(lineStart.x(),
                lineStart.y() + fontMetric.height())
        authorWidth = fontMetric.width(comment[1])
        authorEnd = QPoint(authorStart.x() + authorWidth,
                authorStart.y())
        self.drawAuthorDate(comment, painter, pen, authorStart,
                authorEnd)

        painter.restore()


    def createEditor(self, parent, option, index):

        """ Makes the comment and the author available in a QLineEdit """

        global author

        modAuthor = ""
        if util.isAuthorSet():
            modAuthor = util.getAuthor()
        else:
            openAuthorsDialog(None)
            modAuthor = util.getAuthor()

        comment = index.model().data(index, Qt.EditRole)
        editor = QLineEdit(comment[0], parent)
        editor.setFrame(True)

        return editor


    def setEditorData(self, editor, index):

        """ Updates the editor data with the data at `index` in the model """

        comment = index.model().data(index, Qt.EditRole)
        editorText = comment[0]
        editor.setText(editorText)


    def setModelData(self, editor, model, index):

        """ Updates the model at `index` with the current text of the editor """

        text = editor.text()
        author = util.getAuthor()
        success = model.setData(index, (text, author))
        if not success:
            util.showError("The comment hast to be separated by '--' from the" \
                    " email address!")
            logger.error("Here we have an invalid string")


    def sizeHint(self, option, index):

        """ Return the size of a comment element. """

        comment = index.model().data(index, Qt.DisplayRole)

        # recompute the size hint if the size changed (element == `None`) or
        # compute it for the first time
        if index not in self.sizeHints or self.sizeHints[index] is None:
            size = self.calcCommentSize(comment, option)
            self.sizeHints[index] = size

        size = self.sizeHints[index]
        return size


    def calcCommentSize(self, comment, option = None):

        """ Calculate the size of a comment element.

        The size of comment itself (`comment[0]`) is calculated considering
        wordwrapping. The base rectangle, for calculating the bounding rectangle
        of comment is constructed from the height given by `option.rect` and the
        width set by `setWidth`.
        Thus the size of comment wont exceed the width of the widget.
        """

        authorFontMetric = QFontMetrics(self.authorFont)
        commentBoundRect = self.getCommentRect(comment, option)

        commentTextHeight = commentBoundRect.height()
        authorTextHeight = authorFontMetric.height()

        commentWidth = commentBoundRect.width()
        authorDateWidth = 0
        if comment[1] is not None:
            authorDateWidth = authorFontMetric.width(comment[1] + comment[2]) + self._authorDateQSeparation
            authorDateWidth += self._authorDateQSeparation
        else:
            authorDateWidth = authorFontMetric.width(comment[2])

        # +1 is the separation line that is drawn
        # commentTextHeight / 2 is the offset from the comment text towards the
        # separation line
        height = (commentTextHeight + authorTextHeight +
                self._verticalQOffset + self._commentYQOffset +
                self._separationLineQThickness)
        width = commentWidth if commentWidth > authorDateWidth else authorDateWidth

        size = QSize(width, height)
        return size


    def getCommentRect(self, comment, option = None):

        """ Returns the rectangle where just the comment fits in.

        The comment hereby is wordwrapped and won't exceed the widgets width.
        """

        commentFontMetric = QFontMetrics(self.commentFont)

        # calculate the bounding rectangle for comment that fits into the
        # width of the widget.
        rect = None
        if option is not None:
            rect = self.getWidgetWithRect(option)
        else:
            rect = QRect(0, 0, self.width - self._commentXQOffset,
                    self._maxCommentHeight)

        boundRect = commentFontMetric.boundingRect(rect,
                Qt.TextWordWrap | Qt.AlignLeft,
                comment[0])
        return boundRect


    def getWidgetWithRect(self, option):

        """ Returns a rectangle based on `option.rect` where width is replaced
        by `self.width` """

        rect = option.rect
        rect.setWidth(self.width)
        rect.setHeight(self._maxCommentHeight)

        return rect


    def computeSizes(self):

        screen = util.getCurrentQScreen()
        # pixels per millimeter
        ppm = screen.logicalDotsPerInch() / util.MMPI

        self._commentYQOffset = self._commentYOffset * ppm
        self._commentXQOffset  = self._commentXOffset * ppm
        self._separationLineQThickness = self._separationLineThickness * ppm
        self._verticalQOffset = self._verticalOffset * ppm
        self._maxCommentHeight = screen.size().height()
        self._authorDateQSeparation = self._authorDateSeparation * ppm


    def drawComment(self, comment, painter, option, fontMetric, leftX, topY, brush):

        painter.save()
        pen = painter.pen()
        pen.setColor(brush.color())
        painter.setPen(pen)
        #painter.setFont(self.commentFont)

        commentBoundRect = self.getCommentRect(comment, option)
        commentBoundRect.setX(leftX + self._commentXQOffset)
        commentBoundRect.setY(commentBoundRect.y() + self._commentYQOffset)
        commentBoundRect.setWidth(commentBoundRect.width() -
                self._commentXQOffset)
        commentBoundRect.setHeight(commentBoundRect.height() +
                self._verticalQOffset)

        painter.drawText(commentBoundRect,
                Qt.TextWordWrap | Qt.AlignLeft,
                comment[0])

        painter.restore()
        return commentBoundRect.bottomLeft(), commentBoundRect.height()


    def drawSeparationLine(self, painter, pen, start: QPoint, width):

        end = QPoint(start.x() + width,
                start.y() + self._separationLineQThickness)
        separationRect = QRect(start, end)
        painter.fillRect(separationRect, QColor("lightGray"))


    def drawAuthorDate(self, comment,
            painter, pen,
            start: QPoint, end: QPoint):

        fontMetric = QFontMetrics(self.authorFont)
        pen.setColor(QColor("#666699"))
        painter.setPen(pen)
        painter.setFont(self.authorFont)
        painter.drawText(start, comment[1])

        dateStart = QPoint(end.x(), end.y())
        if comment[1] is not None and len(comment[1]) > 0:
            dateStart.setX(dateStart.x() + self._authorDateQSeparation)

        painter.drawText(dateStart, comment[2])


    def updateFonts(self, baseFont):

        """ Set the internal fonts to baseFont and update their sizes """

        self.commentFont = copy(baseFont)
        self.commentFont.setBold(True)
        self.commentFont.setPointSize(self.baseFontSize)

        self.authorFont = copy(baseFont)
        self.authorFont.setPointSize(self.baseFontSize - 4)


    @Slot()
    def setWidth(self, newWidth):

        self.width = newWidth
        self.checkSizes()


    def checkSizes(self):

        """ Computes the sizes of comment elements, and emits the
        `sizeHintChanged` signal if that is the case. """

        indices = self.sizeHints.keys()
        for index in indices:
            comment = index.model().data(index, Qt.DisplayRole)
            # the comment does not exist anymore
            if comment is None:
                del self.sizeHints[index]
                return

            newHeight = self.calcCommentSize(comment).height()
            oldHeight = None
            if self.sizeHints[index] is not None: # prevent errors due to race conditions
                oldHeight = self.sizeHints[index].height()

            if newHeight != oldHeight:
                self.sizeHintChanged.emit(index)
                # mark the changed size hint for recomputation
                self.sizeHints[index] = None
