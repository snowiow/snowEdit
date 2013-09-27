#!/usr/bin/env
#-*- coding: utf-8 -*-

from PySide import QtGui, QtCore


class SeConsole(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.createComponents()
        self.createLayout()
        self.createConnects()

        self.show()

    def writeToConsole(self, string, error=False):
        selection = QtGui.QTextEdit.ExtraSelection()
        selection.cursor = self.content.textCursor()
        selection.cursor.select(QtGui.QTextCursor.Document)
        selection.cursor.deleteChar()
        selection.cursor.clearSelection()
        if error:
            self.content.setTextColor(QtGui.QColor(QtCore.Qt.red))
        else:
            self.content.setTextColor(QtGui.QColor(QtCore.Qt.black))
        self.content.insertPlainText(string)


    def createComponents(self):
        self.content = QtGui.QTextEdit(self)
        self.content.setReadOnly(True)
        self.contentScrollbar = QtGui.QScrollBar(self)
        self.content.setVerticalScrollBar(self.contentScrollbar)

        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.addTab(self.content, 'Console')
        self.tabWidget.setTabIcon(0, QtGui.QIcon(':icons/compilerOptions.png'))

    def createLayout(self):
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)

    def createConnects(self):
        pass
