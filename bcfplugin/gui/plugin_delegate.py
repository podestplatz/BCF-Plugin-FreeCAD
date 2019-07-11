from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import (QModelIndex, Slot, QSize, QPoint, Signal, Qt)

from copy import copy


commentRegex = "[a-zA-Z0-9.,\-\/ ]* -- .*@.*"

class CommentDelegate(QStyledItemDelegate):

    invalidInput = Signal((QModelIndex,))

    def __init__(self, parent = None):

        QStyledItemDelegate.__init__(self, parent)
        self.baseFontSize = 12
        self.commentFont = QFont("times")
        self.updateFonts(self.commentFont)

        self.commentYOffset = 10


    def paint(self, painter, option, index):

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        idx = index.row()

        comment = index.model().data(index, Qt.DisplayRole)
        # top y coordinate at which drawing will begin downwards
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
        commentTextHeight = fontMetric.height()
        commentTextWidth = fontMetric.width(comment[0])
        commentStart = QPoint(10, topY + fontMetric.height())
        painter.drawText(commentStart, comment[0])

        # draw separation line
        pen.setColor(QColor("lightGray"))
        painter.setPen(pen)
        lineStart = QPoint(commentStart.x(),
                commentStart.y() + commentTextHeight / 2)
        lineEnd = QPoint(lineStart.x() + boundingRect.width() - 20,
                lineStart.y())
        painter.drawLine(lineStart, lineEnd)

        # draw author
        fontMetric = QFontMetrics(self.authorFont)
        pen.setColor(QColor("blue"))
        painter.setPen(pen)
        painter.setFont(self.authorFont)
        authorStart = QPoint(lineStart.x(),
                lineStart.y() + fontMetric.height())
        authorWidth = fontMetric.width(comment[1])
        authorEnd = QPoint(authorStart.x() + authorWidth,
                authorStart.y())
        painter.drawText(authorStart, comment[1])

        dateStart = QPoint(authorEnd.x() + 10, authorEnd.y())
        painter.drawText(dateStart, comment[2])

        painter.restore()


    def createEditor(self, parent, option, index):

        """ Makes the comment and the author available in a QLineEdit """

        comment = index.model().data(index, Qt.EditRole)
        startText = comment[0] + " -- " + comment[1]

        validator = QRegExpValidator()
        validator.setRegExp(commentRegex)
        editor = QLineEdit(startText, parent)
        editor.setValidator(validator)
        editor.setFrame(True)

        return editor


    def setEditorData(self, editor, index):

        """ Updates the editor data with the data at `index` in the model """

        comment = index.model().data(index, Qt.EditRole)
        editorText = comment[0] + " -- " + comment[1]
        editor.setText(editorText)


    def setModelData(self, editor, model, index):

        """ Updates the model at `index` with the current text of the editor """

        text = editor.text()
        success = model.setData(index, text)
        if not success:
            util.showError("The comment hast to be separated by '--' from the" \
                    " email address!")
            util.printError("Here we have an invalid string")


    def updateFonts(self, baseFont):

        """ Set the internal fonts to baseFont and update their sizes """

        self.commentFont = copy(baseFont)
        self.commentFont.setBold(True)
        self.commentFont.setPointSize(self.baseFontSize)

        self.authorFont = copy(baseFont)
        self.authorFont.setPointSize(self.baseFontSize - 4)


    def calcCommentSize(self, comment, option):

        """ Calculate the size of a comment element """

        commentFontMetric = QFontMetrics(self.commentFont)
        authorFontMetric = QFontMetrics(self.authorFont)

        commentTextHeight = commentFontMetric.height()
        authorTextHeight = authorFontMetric.height()

        # +1 is the separation line that is drawn
        # commentTextHeight / 2 is the offset from the comment text towards the
        # separation line
        height = (commentTextHeight + authorTextHeight +
                commentTextHeight / 2 + self.commentYOffset + 1)
        width = option.rect.width()

        size = QSize(width, height)
        return size


    def sizeHint(self, option, index):

        """ Return the size of a comment element. """

        comment = index.model().data(index, Qt.DisplayRole)
        size = self.calcCommentSize(comment, option)

        return size
