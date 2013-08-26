#-*- coding: utf-8 -*-

from PySide import QtCore, QtGui


class RaschHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        QtGui.QSyntaxHighlighter.__init__(self, parent)

        self.createKeywords()
        self.createOperators()
        self.createClassVariables()
        self.createStrings()
        self.createSingleLineComments()
        self.createAnnotations()

    def createKeywords(self):
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.darkBlue)
        keywordFormat.setFontWeight(QtGui.QFont.Bold)

        keywords = []