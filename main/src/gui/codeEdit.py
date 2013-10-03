#-*- coding: utf-8 -*-

import re

from PySide import QtGui, QtCore
from lineNumberArea import LineNumberArea
from seCompletion import SeCompletion

from highlighter.highlighterHelpFunction import *

from ..resources.rc_snowedit import *

from ..util.helperFunctions import normalizeSeps
from ..util.iniManager import IniManager
from ..util.RaschLexer import RaschLexer


class CodeEdit(QtGui.QPlainTextEdit):

    def __init__(self, tabWidget, filePath=None):
        QtGui.QPlainTextEdit.__init__(self)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.lineNumberArea = LineNumberArea(self)
        self.tabWidget = tabWidget
        self.completion = None
        self.lexer = RaschLexer()

        self.errorRegEx = re.compile('(\(\d+\))')

        self.createMenu()
        self.createComponents()
        self.createConnects()

        self.updateLineNumberAreaWidth()
        self.updateOptions()
        if filePath is not None:
            self.filePath = normalizeSeps(filePath)
            try:
                f = open(str(filePath), 'r')
                fileData = f.read()
                self.setPlainText(fileData)
                f.close()
            except IOError:
                QtGui.QMessageBox.critical(self, 'Error',
                                           'Error, while saving file',
                                           QtGui.QMessageBox.Ok)

            self.highlighter = chooseHighlighter(
                self.document(), self.filePath)

        else:
            self.filePath = 'new file'
            self.highlighter = chooseHighlighter(
                self.document(), self.filePath)

    # Slots
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
            self.lineNumberArea.update(
                0, qRect.y(), self.lineNumberArea.width(), qRect.height())

        if qRect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth()

    @QtCore.Slot()
    def highlightCurrentLine(self,
                             color=QtGui.QColor(QtCore.Qt.yellow).lighter(160)):
        extraSelections = []

        if not self.isReadOnly():
            selection = QtGui.QTextEdit.ExtraSelection()

            selection.format.setBackground(color)
            selection.format.setProperty(
                QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    @QtCore.Slot()
    def insertCompletion(self, completion):
        cursor = self.textCursor()
        extra = (len(completion) -
                 len(self.completion.completionPrefix()))

        #cursor.movePosition(QtGui.QTextCursor.Left)
        cursor.movePosition(QtGui.QTextCursor.EndOfWord)
        cursor.insertText(completion[len(completion) - extra:])
        self.setTextCursor(cursor)

    def textUnderCursor(self):
        prefix = ''

        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.StartOfWord)
        cursor.movePosition(QtGui.QTextCursor.PreviousCharacter)
        cursor.select(QtGui.QTextCursor.WordUnderCursor)
        if cursor.selectedText() == '$':
            prefix = '$'
        elif cursor.selectedText() == '@':
            prefix = '@'

        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.WordUnderCursor)
        return prefix + cursor.selectedText()


    def focusInEvent(self, event):
        if self.completion:
            self.completion.setWidget(self)
        QtGui.QPlainTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        if self.completion and self.completion.popup().isVisible():
            if event.key() in (
                QtCore.Qt.Key_Enter,
                QtCore.Qt.Key_Return,
                QtCore.Qt.Key_Escape,
                QtCore.Qt.Key_Tab,
                QtCore.Qt.Key_Backtab):
                event.ignore()
                return

        isShortCut = (event.modifiers() == QtCore.Qt.ControlModifier and
                      event.key() == QtCore.Qt.Key_Space)

        if not self.completion or not isShortCut:
            QtGui.QPlainTextEdit.keyPressEvent(self, event)

        ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier,
                                            QtCore.Qt.ShiftModifier)

        if ctrlOrShift and event.text() == '':
            return

        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="

        hasModifiers = ((event.modifiers() != QtCore.Qt.NoModifier) and
                        not ctrlOrShift)

        completionPrefix = self.textUnderCursor()

        if not isShortCut and (hasModifiers or event.text() == '' or len(
                completionPrefix) < 3 or eow.find(event.text()[:1]) != -1):
            self.completion.popup().hide()
            return

        if completionPrefix != self.completion.completionPrefix():
            self.completion.setCompletionPrefix(completionPrefix)
            popup = self.completion.popup()
            popup.setCurrentIndex(
                self.completion.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self.completion.popup().sizeHintForColumn(0)
                    + self.completion.popup().verticalScrollBar().
        sizeHint().width())
        self.completion.complete(cr)

    def highlightErrorLine(self, lineNumber):

        textBlock = QtGui.QTextCursor(self.document().findBlockByLineNumber(
            lineNumber - 1))
        textCursor = QtGui.QTextCursor(self.textCursor())
        textCursor.setPosition(textBlock.position())
        self.setTextCursor(textCursor)

        self.highlightCurrentLine(color=QtGui.QColor(QtCore.Qt.red))

    def createMenu(self):
        # Context Menu Actions
        self.undoAction = QtGui.QAction(
            QtGui.QIcon(':icons/undo.png'), 'Undo', self)
        self.undoAction.setShortcut(QtGui.QKeySequence.Undo)

        self.redoAction = QtGui.QAction(
            QtGui.QIcon(':icons/redo.png'), 'Redo', self)
        self.redoAction.setShortcut(QtGui.QKeySequence.Redo)

        self.cutAction = QtGui.QAction(
            QtGui.QIcon(':icons/cut.png'), 'Cut', self)
        self.cutAction.setShortcut(QtGui.QKeySequence.Cut)

        self.copyAction = QtGui.QAction(
            QtGui.QIcon(':icons/copy.png'), 'Copy', self)
        self.copyAction.setShortcut(QtGui.QKeySequence.Copy)

        self.pasteAction = QtGui.QAction(
            QtGui.QIcon(':icons/paste.png'), 'Paste', self)
        self.pasteAction.setShortcut(QtGui.QKeySequence.Paste)

        self.duplicateLineAction = QtGui.QAction(
            QtGui.QIcon(':icons/duplicate-line.png'), 'Duplicate current line',
            self)
        self.duplicateLineAction.setShortcut('Ctrl+D')

        self.commentLineAction = QtGui.QAction(
            QtGui.QIcon(':icons/comment.png'),
            '(De-)comment current line', self)
        self.commentLineAction.setShortcut('Ctrl+7')

        # Add actions to menu
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

    def createComponents(self):
        completer = SeCompletion()
        completer.setWidget(self)
        self.completion = completer

    def createConnects(self):
        # Context Menu Events
        self.connect(self, QtCore.SIGNAL('customContextMenuRequested(QPoint)'),
                     self, QtCore.SLOT('contextMenu(QPoint)'))

        self.undoAction.triggered.connect(self.undo)
        self.redoAction.triggered.connect(self.redo)
        self.cutAction.triggered.connect(self.cut)
        self.copyAction.triggered.connect(self.copy)
        self.pasteAction.triggered.connect(self.paste)
        self.duplicateLineAction.triggered.connect(self.duplicateLine)
        self.commentLineAction.triggered.connect(self.commentLine)

        # Editor behaviour events
        self.connect(self, QtCore.SIGNAL('blockCountChanged(int)'),
                     self.updateLineNumberAreaWidth)

        self.connect(self, QtCore.SIGNAL('updateRequest(QRect, int)'),
                     self.updateLineNumberArea)

        self.connect(self, QtCore.SIGNAL('cursorPositionChanged()'),
                     self, QtCore.SLOT('highlightCurrentLine()'))

        self.connect(self, QtCore.SIGNAL('textChanged()'),
                     self.tabWidget, QtCore.SLOT('starTab()'))

        self.connect(self.completion,
                     QtCore.SIGNAL("activated(const QString&)"),
                     self.insertCompletion)

    # Update Editor behaviour after modifieing settings
    def updateOptions(self):
        if IniManager.getInstance().readBoolean('Editor', 'showlinenumbers'):
            self.lineNumberArea.show()
        else:
            self.lineNumberArea.hide()

        if IniManager.getInstance().readBoolean('Editor',
                                                'highlightcurrentline'):
            self.highlightCurrentLine()
        else:
            self.highlightCurrentLine(QtGui.QColor())

        font = IniManager.getInstance().getFont()

        self.setFont(font)

        tabSize = IniManager.getInstance().readInt('Editor', 'tabSize')
        metrics = QtGui.QFontMetrics(font)
        self.setTabStopWidth(tabSize * metrics.width(' '))

        self.update()

    def lineNumberAreaWidth(self):
        digits = 1
        myMax = max(1, self.blockCount())

        while myMax >= 10:
            myMax /= 10
            digits += 1

        space = 5 + self.fontMetrics().width('9') * digits
        return space

    def resizeEvent(self, qResizeEvent):
        QtGui.QPlainTextEdit.resizeEvent(self, qResizeEvent)

        contentsRect = self.contentsRect()
        if IniManager.getInstance().readBoolean('Editor', 'showlinenumbers'):
            self.lineNumberArea.setGeometry(
                QtCore.QRect(contentsRect.left(), contentsRect.top(),
                             self.lineNumberAreaWidth(),
                             contentsRect.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self.lineNumberArea)
        painter.fillRect(
            event.rect(), QtGui.QColor(QtCore.Qt.blue).lighter(170))

        qTextBlock = self.firstVisibleBlock()
        blockNumber = qTextBlock.blockNumber()
        top = int(self.blockBoundingGeometry(qTextBlock)
                  .translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(qTextBlock).height())

        while qTextBlock.isValid() and top <= event.rect().bottom():
            if qTextBlock.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QtCore.Qt.black)
                painter.drawText(
                    0, top, self.lineNumberArea.width(
                    ), self.fontMetrics().height(),
                    QtCore.Qt.AlignRight, number)

            qTextBlock = qTextBlock.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(qTextBlock).height())
            blockNumber += 1

    def generateError(self, output):
        result = re.search(self.errorRegEx, output)
        if result is not None:
            results = result.groups()
            for line in results:
                number = line.split('(')[1].split(')')[0]
                self.highlightErrorLine(int(number))

    def updateCompleter(self):
        variables = []
        if self.toPlainText() is not '':
            variables = self.lexer.getVariables(self.toPlainText())

        self.completion.addWords(variables)


