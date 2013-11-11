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
        """
        Code Edit is a advanced QPlaintextEdit with IDE features, like line
        numbers, line highlighting, tabs interpreted as spaces, completion etc.
        """
        QtGui.QPlainTextEdit.__init__(self)

        #privates
        self._updateCounter = 0
        self._avgWordLength = 0

        self._completer = None

        self._lineNumberArea = LineNumberArea(self)
        self._lexer = RaschLexer()
        self._errorRegEx = re.compile('(\(\d+\))')

        #publics
        self.tabWidget = tabWidget

        #Set Custom ContextMenu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        #Create the code editor
        self.createMenu()
        self.createComponents()
        self.createConnects()

        self.updateOptions()

        #if a filePath parameter is given, paste the content into lineEdit
        #and save the path into a variable
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
    def updateCompleter(self):
        """
        If the codeEdit isn't empty, the text will be parsed and the
        completer will be updated with the current set variables in the file
        """
        variables = []
        if self.toPlainText() is not '':
            variables = self._lexer.getVariables(self.toPlainText())

        self._completer.updateWords(variables)

    @QtCore.Slot()
    def checkCompleteUpdate(self):
        """
        Checks if the average word length is reached. If true it calls the
        updateCompleter method and resets the counter and a new average word
        length
        """
        self.updateCompleter()

    @QtCore.Slot()
    def duplicateLine(self):
        """Edit Feature to duplicate the current line"""
        selection = QtGui.QTextEdit.ExtraSelection()
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        selection.cursor.select(QtGui.QTextCursor.LineUnderCursor)

        content = selection.cursor.selectedText()
        selection.cursor.clearSelection()
        self.insertPlainText("\n" + content)

    @QtCore.Slot()
    def commentLine(self):
        """Edit Feature to comment current line or the whole selection"""
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
        """Open the ContextMenu at current mouse position"""
        self.menu.exec_(self.mapToGlobal(pos))

    @QtCore.Slot()
    def updateLineNumberAreaWidth(self):
        """ Updates the area of the line Number Area"""
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    @QtCore.Slot()
    def updateLineNumberArea(self, qRect, dy):
        """updates the area of the line numbers"""
        if dy:
            self._lineNumberArea.scroll(0, dy)
        else:
            self._lineNumberArea.update(
                0, qRect.y(), self._lineNumberArea.width(), qRect.height())

        if qRect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth()

    @QtCore.Slot()
    def highlightCurrentLine(self,
                             color=QtGui.QColor(QtCore.Qt.yellow).lighter(160)):

        """highlight line where the cursor is placed"""
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
        """
        calculates the word prefix and appends the rest of the chosen word from
        completion
        """
        cursor = self.textCursor()
        extra = (len(completion) -
                 len(self._completer.completionPrefix()))

        #cursor.movePosition(QtGui.QTextCursor.Left)
        cursor.movePosition(QtGui.QTextCursor.EndOfWord)
        cursor.insertText(completion[len(completion) - extra:])

    def textUnderCursor(self):
        """
        Returns the word under the cursor + the prefix ($ or @) if there is one
        """
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
        """
        Overwrite of focusInEvent, that the completer directly
        gets the focus if popping up
        """
        if self._completer:
            self._completer.setWidget(self)
        QtGui.QPlainTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        """
        Ignore cases of wrong keys and modifiers. Afterwards prepare correct
        completion popup
        """
        if self._completer and self._completer.popup().isVisible():
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

        if not self._completer or not isShortCut:
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
            self._completer.popup().hide()
            return

        if completionPrefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completionPrefix)
            popup = self._completer.popup()
            popup.setCurrentIndex(
                self._completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self._completer.popup().sizeHintForColumn(0)
                    + self._completer.popup().verticalScrollBar().
        sizeHint().width())
        self._completer.complete(cr)

    def highlightErrorLine(self, lineNumber):
        """
        Color the line in red where an error occurred and place the
        cursor in that line
        """
        textBlock = QtGui.QTextCursor(self.document().findBlockByLineNumber(
            lineNumber - 1))
        textCursor = QtGui.QTextCursor(self.textCursor())
        textCursor.setPosition(textBlock.position())
        self.setTextCursor(textCursor)

        self.highlightCurrentLine(color=QtGui.QColor(QtCore.Qt.red))

    def createMenu(self):
        """Create the context menu options"""
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
        """
        Create the components of the editor
        """
        completer = SeCompletion()
        completer.setWidget(self)
        self._completer = completer

    def createConnects(self):
        """ Create all necessary connects of the codeEditor"""
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

        self.connect(self._completer,
                     QtCore.SIGNAL('activated(const QString&)'),
                     self.insertCompletion)

        self.connect(self, QtCore.SIGNAL('textChanged()'),
                     self.checkCompleteUpdate)

    def updateOptions(self):
        """adjust the editor to the settings of the config file"""
        self.updateLineNumberAreaWidth()

        if IniManager.getInstance().readBoolean('Editor', 'showlinenumbers'):
            self._lineNumberArea.show()
        else:
            self._lineNumberArea.hide()

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

    def resizeEvent(self, qResizeEvent):
        """
        overwrite the resizeEvent to resize the lineNumberArea appropriate to
        the editor itself
        """
        QtGui.QPlainTextEdit.resizeEvent(self, qResizeEvent)

        contentsRect = self.contentsRect()
        if IniManager.getInstance().readBoolean('Editor', 'showlinenumbers'):
            self._lineNumberArea.setGeometry(
                QtCore.QRect(contentsRect.left(), contentsRect.top(),
                             self.lineNumberAreaWidth(),
                             contentsRect.height()))

    def lineNumberAreaWidth(self):
        """
        calculates the width of the line number area
        """
        digits = 1
        myMax = max(1, self.blockCount())

        while myMax >= 10:
            myMax /= 10
            digits += 1

        space = 5 + self.fontMetrics().width('9') * digits
        return space

    def lineNumberAreaPaintEvent(self, event):
        """
        Create the line number area, set its color and draw the needed line
        numbers
        """
        painter = QtGui.QPainter(self._lineNumberArea)
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
                    0, top, self._lineNumberArea.width(
                    ), self.fontMetrics().height(),
                    QtCore.Qt.AlignRight, number)

            qTextBlock = qTextBlock.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(qTextBlock).height())
            blockNumber += 1

    def generateError(self, output):
        """search for the error lines and call the highlightErrorLine method"""
        result = re.search(self._errorRegEx, output)
        if result is not None:
            results = result.groups()
            for line in results:
                number = line.split('(')[1].split(')')[0]
                self.highlightErrorLine(int(number))




