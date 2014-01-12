from PySide import QtGui, QtCore


class SeFind(QtGui.QWidget):

    def __init__(self, currentEditor):
        QtGui.QWidget.__init__(self)

        self.currentEditor = currentEditor
        self.isFirstTime = True

        self.createComponents()
        self.createLayout()
        self.createConnects()
        self.hide()

    @QtCore.Slot()
    def onSearchButtonClicked(self):
        if self._searchLE.text().startswith('@'):
            if self._searchLE.text().rsplit('@', 1)[1].isdecimal():
                self.goto()
            else:
                self.search()
        else:
            self.search()

    @QtCore.Slot()
    def onCancelButtonClicked(self):
        if self.isFirstTime == False:
            self.currentEditor.document().undo()
        self.hide()

    def search(self):
        if self._searchLE.text():
            currentPosition = self.currentEditor.textCursor()
            highlightCursor = self.currentEditor.textCursor()
            highlightCursor.movePosition(QtGui.QTextCursor.Start)

            plainFormat = highlightCursor.charFormat()
            colorFormat = plainFormat
            colorFormat.setForeground(QtCore.Qt.darkCyan)
            colorFormat.setFontItalic(True)
            colorFormat.setFontWeight(QtGui.QFont.Bold)

            if self.isFirstTime == False:
                self.currentEditor.document().undo()

            currentPosition.beginEditBlock()

            while not highlightCursor.isNull() and not highlightCursor.atEnd():
                highlightCursor = \
                    self.currentEditor.document().find(self._searchLE.text(),
                                                       highlightCursor)
                if not highlightCursor.isNull():
                    highlightCursor.movePosition(QtGui.QTextCursor.EndOfWord,
                                                 QtGui.QTextCursor.KeepAnchor)
                    highlightCursor.mergeCharFormat(colorFormat)
                    self.isFirstTime = False

            currentPosition.endEditBlock()

    def goto(self):
        if self.isFirstTime == False:
            self.currentEditor.document().undo()

        lineStr = self._searchLE.text().rsplit('@', 1)[1]
        try:
            line = int(lineStr)
        except ValueError:
            print "error"
            return

        textBlock = QtGui.QTextCursor(self.currentEditor.document().
                    findBlockByLineNumber(line - 1))
        textCursor = QtGui.QTextCursor(self.currentEditor.textCursor())
        textCursor.setPosition(textBlock.position())
        self.currentEditor.setTextCursor(textCursor)
        self.currentEditor.setFocus()
        self.onCancelButtonClicked()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.onCancelButtonClicked()

    def createComponents(self):
        self._searchLabel = QtGui.QLabel('Search for', self)
        self._searchLE = QtGui.QLineEdit(self)
        self._searchButton = QtGui.QPushButton('Search', self)
        self._searchButton.setDefault(True)
        self._searchButton.setAutoDefault(True)

        self._cancelButton = QtGui.QPushButton()
        self._cancelButton.setFlat(True)
        self._cancelButton.setIcon(QtGui.QIcon(':icons/cancel.png'))

    def createLayout(self):
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self._searchLabel)
        layout.addWidget(self._searchLE, 3)
        layout.addWidget(self._searchButton)
        layout.addWidget(self._cancelButton)
        self.setLayout(layout)

    def createConnects(self):
        self._searchButton.clicked.connect(self.onSearchButtonClicked)
        self._cancelButton.clicked.connect(self.onCancelButtonClicked)

        self.connect(self._searchLE, QtCore.SIGNAL('returnPressed()'),
                     self, QtCore.SLOT('onSearchButtonClicked()'))