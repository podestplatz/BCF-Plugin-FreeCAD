from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QModelIndex, Slot, QSize, QRect, QPoint, QRectF

from copy import copy


class CommentDelegate(QStyledItemDelegate):

    def __init__(self, parent = None):

        QStyledItemDelegate.__init__(self, parent)
        self.commentFont = QFont("times", 12)
        self.authorFont = self.commentFont
        self.authorFont.setPixelSize(self.authorFont.pixelSize() - 2)

        self.lastBottomY = 0
        self.commentYOffset = 10


    def paint(self, painter, option, index):

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())


        comment = index.model().data(index, Qt.DisplayRole)
        topY = self.lastBottomY * index.row() + self.commentYOffset

        painter.save()

        boundingRect = painter.viewport()
        pen = painter.pen()
        self.updateFonts(painter.font())
        fontMetric = painter.fontMetrics()
        painter.setBrush(option.palette.text())

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
        self.lastBottomY = dateStart.y()


    def createEditor(self, parent, option, index):

        comment = index.model().data(index, Qt.EditRole)
        startText = comment[0] + " -- " + comment[1]

        editor = QLineEdit(startText, parent)
        editor.setFrame(True)

        return editor


    def setEditorData(self, editor, index):

        comment = index.model().data(index, Qt.EditRole)
        editorText = comment[0] + " -- " + comment[1]
        editor.setText(editorText)


    def setModelData(self, editor, model, index):

        text = editor.text()
        splitText = [ textItem.strip() for textItem in text.split("--") ]
        if len(splitText) != 2:
            #TODO raise/display an exception
            print("Here we have an invalid string")
            return

        success = model.setData(index, (splitText[0], splitText[1]))
        if not success:
            print("Well that did not work")


    def updateFonts(self, baseFont):

        baseSize = 14

        self.commentFont = copy(baseFont)
        self.commentFont.setBold(True)
        self.commentFont.setPixelSize(baseSize)

        self.authorFont = copy(baseFont)
        self.authorFont.setPixelSize(baseSize - 2)


    def calcCommentSize(self, comment, option):

        commentFontMetric = QFontMetrics(self.commentFont)
        authorFontMetric = QFontMetrics(self.authorFont)

        commentTextHeight = commentFontMetric.height()
        authorTextHeight = authorFontMetric.height()

        height = (commentTextHeight + authorTextHeight +
                commentTextHeight / 2 + self.commentYOffset)
        width = option.rect.width()

        size = QSize(width, height)
        return size


    def sizeHint(self, option, index):

        comment = index.model().data(index, Qt.DisplayRole)
        size = self.calcCommentSize(comment, option)

        return size
