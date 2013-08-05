#-*- coding: utf-8 -*-

import os

from PySide import QtGui, QtCore
from lineNumberArea import LineNumberArea
from seTabWidget import SeTabWidget
from ..resources.rc_snowedit import *
from ..util.iniManager import IniManager


class CodeEdit(QtGui.QPlainTextEdit):
    def __init__(self, tabWidget, filePath=None):
        QtGui.QPlainTextEdit.__init__(self)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.lineNumberArea = LineNumberArea(self)
        self.tabWidget = tabWidget

        self.createMenu()
        self.createConnects()

        self.updateLineNumberAreaWidth()
        self.updateOptions()

        if filePath is not None:
            self.filePath = filePath
            try:
                file = open(str(filePath), 'r')
                fileData = file.read()
                self.setPlainText(fileData)
                file.close()
            except IOError as e:
                QtGui.QMessageBox.critical(self, 'Error', 'Error, while saving file', QtGui.QMessageBox.Ok)
        else:
            self.filePath = 'new file'

    #Slots

    @QtCore.Slot()
    def duplicateLine(self):

        selection = QtGui.QTextEdit.ExtraSelection()
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        selection.cursor.select(QtGui.QTextCursor.LineUnderCursor)

        content = selection.cursor.selectedText()
        selection.cursor.clearSelection()
        self.insertPlainText("\n" + content)

    @QtCore.Slot()
    def commentLine(self):

        selection = QtGui.QTextEdit.ExtraSelection()

        currentPosition = self.textCursor()
        selection.cursor = self.textCursor()

        selection.cursor.select(QtGui.QTextCursor.LineUnderCursor)
        lineText = selection.cursor.selectedText()
        selection.cursor.clearSelection()

        selection.cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        self.setTextCursor(selection.cursor)

        if lineText.startswith('//'):
            selection.cursor.deleteChar()
            selection.cursor.deleteChar()
        else:
            self.insertPlainText('//')

        self.setTextCursor(currentPosition)

    @QtCore.Slot(QtCore.QPoint)
    def contextMenu(self, pos):
        self.menu.exec_(self.mapToGlobal(pos))

    @QtCore.Slot()
    def updateLineNumberAreaWidth(self):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    @QtCore.Slot()
    def updateLineNumberArea(self, qRect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, qRect.y(), self.lineNumberArea.width(), qRect.height())

        if qRect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth()

    @QtCore.Slot()
    def highlightCurrentLine(self, color):
        extraSelections = []

        if not self.isReadOnly():
            selection = QtGui.QTextEdit.ExtraSelection()

            lineColor = color

            selection.format.setBackground(lineColor)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    @property
    def fileName(self):
        if self.filePath.find(os.sep) != -1:
            return self.filePath.rsplit(os.sep, 1)[1]
        elif self.filePath.find('/') != -1:
            return self.filePath.rsplit('/', 1)[1]
        return self.filePath

    def createMenu(self):
        #Context Menu Actions
        self.undoAction = QtGui.QAction(QtGui.QIcon(':icons/undo.png'), 'Undo', self)
        self.undoAction.setShortcut(QtGui.QKeySequence.Undo)

        self.redoAction = QtGui.QAction(QtGui.QIcon(':icons/redo.png'), 'Redo', self)
        self.redoAction.setShortcut(QtGui.QKeySequence.Redo)

        self.cutAction = QtGui.QAction(QtGui.QIcon(':icons/cut.png'), 'Cut', self)
        self.cutAction.setShortcut(QtGui.QKeySequence.Cut)

        self.copyAction = QtGui.QAction(QtGui.QIcon(':icons/copy.png'), 'Copy', self)
        self.copyAction.setShortcut(QtGui.QKeySequence.Copy)

        self.pasteAction = QtGui.QAction(QtGui.QIcon(':icons/paste.png'), 'Paste', self)
        self.pasteAction.setShortcut(QtGui.QKeySequence.Paste)

        self.duplicateLineAction = QtGui.QAction(QtGui.QIcon(':icons/duplicate-line.png'), 'Duplicate current line',
                                                 self)
        self.duplicateLineAction.setShortcut('Ctrl+D')

        self.commentLineAction = QtGui.QAction(QtGui.QIcon(':icons/comment.png'), '(De-)comment current line', self)
        self.commentLineAction.setShortcut('Ctrl+7')

        #Add actions to menu
        self.menu = QtGui.QMenu()
        self.menu.addAction(self.undoAction)
        self.menu.addAction(self.redoAction)
        self.menu.addSeparator()
        self.menu.addAction(self.cutAction)
        self.menu.addAction(self.copyAction)
        self.menu.addAction(self.pasteAction)
        self.menu.addSeparator()
        self.menu.addAction(self.duplicateLineAction)
        self.menu.addAction(self.commentLineAction)

    def createConnects(self):
        #Context Menu Events
        self.connect(self, QtCore.SIGNAL('customContextMenuRequested(QPoint)'),
                     self, QtCore.SLOT('contextMenu(QPoint)'))

        self.undoAction.triggered.connect(self.undo)
        self.redoAction.triggered.connect(self.redo)
        self.cutAction.triggered.connect(self.cut)
        self.copyAction.triggered.connect(self.copy)
        self.pasteAction.triggered.connect(self.paste)
        self.duplicateLineAction.triggered.connect(self.duplicateLine)
        self.commentLineAction.triggered.connect(self.commentLine)

        #Editor behaviour events
        self.connect(self, QtCore.SIGNAL('blockCountChanged(int)'),
                     self.updateLineNumberAreaWidth)

        self.connect(self, QtCore.SIGNAL('updateRequest(QRect, int)'),
                     self.updateLineNumberArea)

        self.connect(self, QtCore.SIGNAL('cursorPositionChanged()'),
                     self.highlightCurrentLine(QtGui.QColor(QtCore.Qt.yellow).lighter(160)))

        self.connect(self, QtCore.SIGNAL('textChanged()'), self.tabWidget, QtCore.SLOT('starTab()'))

    #Update Editor behaviour after modifieing settings
    def updateOptions(self):
        if IniManager.getInstance().readBoolean('Editor', 'showlinenumbers'):
            self.lineNumberArea.show()
        else:
            self.lineNumberArea.hide()

        if IniManager.getInstance().readBoolean('Editor', 'highlightcurrentline'):
            self.highlightCurrentLine(QtGui.QColor(QtCore.Qt.yellow).lighter(160))
        else:
            self.highlightCurrentLine(QtGui.QColor(QtCore.Qt.white))

        font = IniManager.getInstance().getFont()

        self.setFont(font)
        self.update()

    def lineNumberAreaWidth(self):
        digits = 1
        myMax = max(1, self.blockCount())

        while myMax >= 10:
            myMax /= 10
            digits += 1

        space = 3 + self.fontMetrics().width('9') * digits
        return space

    def resizeEvent(self, qResizeEvent):
        QtGui.QPlainTextEdit.resizeEvent(self, qResizeEvent)

        contentsRect = self.contentsRect()
        if IniManager.getInstance().readBoolean('Editor', 'showlinenumbers'):
            self.lineNumberArea.setGeometry(QtCore.QRect(contentsRect.left(), contentsRect.top(),
                                                         self.lineNumberAreaWidth(), contentsRect.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QtGui.QColor(QtCore.Qt.blue).lighter(170))

        qTextBlock = self.firstVisibleBlock()
        blockNumber = qTextBlock.blockNumber()
        top = int(self.blockBoundingGeometry(qTextBlock).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(qTextBlock).height())

        while qTextBlock.isValid() and top <= event.rect().bottom():
            if qTextBlock.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QtCore.Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), self.fontMetrics().height(),
                                 QtCore.Qt.AlignRight, number)

            qTextBlock = qTextBlock.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(qTextBlock).height())
            blockNumber += 1