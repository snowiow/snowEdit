#-*- coding: utf-8 -*-

from PySide import QtCore, QtGui


class RaschHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        QtGui.QSyntaxHighlighter.__init__(self, parent)

        self._multiLineCommentFormat = QtGui.QTextCharFormat()
        self._multiLineCommentFormat.setForeground(QtCore.Qt.lightGray)

        self._commentStartExpression = QtCore.QRegExp("/\\*")
        self._commentEndExpression = QtCore.QRegExp("\\*/")

        self.createKeywords()
        self.createOperators()
        self.createStrings()
        self.createPrefixes()
        self.createArrows()
        self.createComments()

    def createKeywords(self):
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtGui.QColor(64, 155, 11))

        keywords = [
            '\\balias\\b', '\\bas\\b', '\\bconst\\b', '\\bdelete\\b',
            '\\bdo\\b', '\\belse\\b', '\\benum\\b', '\\bfalse\\b',
            '\\bfor\\b', '\\bfunction\\b', '\\bif\\b', '\\bimport\\b',
            '\\bin\\b', '\\bis\\b', '\\bnew\\b', '\\bnull\\b',
            '\\bpackage\\b', '\\bprivate\\b', '\\bprotected\\b',
            '\\bpublic\\b', '\\bref\\b', '\\breturn\\b', '\\bshared\\b',
            '\\bstatic\\b', '\\btemplate\\b', '\\btype\\b', '\\bthis\\b',
            '\\bthrow\\b', '\\btrue\\b', '\\btry\\b', '\\bunion\\b',
            '\\bunique\\b', '\\bwhile\\b', '\\bwith\\b']

        self.highlightingRules = [(QtCore.QRegExp(pattern), keywordFormat)
                                  for pattern in keywords]

    def createOperators(self):
        operatorFormat = QtGui.QTextCharFormat()
        operatorFormat.setForeground(QtGui.QColor(148, 99, 233))
        operatorFormat.setFontWeight(QtGui.QFont.Bold)

        operators = ['\\+', '-', '/', '\\*',
                     '=', '==', '!=', '<=', '>=', '<', '>']

        self.highlightingRules.extend(
            [(QtCore.QRegExp(pattern), operatorFormat) for
             pattern in operators])

    def createStrings(self):
        stringFormat = QtGui.QTextCharFormat()
        stringFormat.setForeground(QtCore.Qt.lightGray)
        self.highlightingRules.append((QtCore.QRegExp('\".*\"'), stringFormat))
        self.highlightingRules.append((QtCore.QRegExp('\'.*\''), stringFormat))

    def createComments(self):
        singleLineCommentFormat = QtGui.QTextCharFormat()
        singleLineCommentFormat.setForeground(QtCore.Qt.gray)
        self.highlightingRules.append(
            (QtCore.QRegExp('//[^\n]*'), singleLineCommentFormat))

    def createPrefixes(self):
        prefixFormat = QtGui.QTextCharFormat()
        prefixFormat.setForeground(QtCore.Qt.darkBlue)

        prefixes = ['\\$[_a-zA-Z0-9]+', '@[_a-zA-Z0-9]+']

        self.highlightingRules.extend(
            [(QtCore.QRegExp(pattern), prefixFormat) for pattern in prefixes])

    def createArrows(self):
        arrowFormat = QtGui.QTextCharFormat()
        arrowFormat.setForeground(QtCore.Qt.red)
        arrows = ['<-', '->']
        self.highlightingRules.extend(
            [(QtCore.QRegExp(pattern), arrowFormat) for pattern in arrows])

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = pattern
            index = expression.indexIn(text)

            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0

        if self.previousBlockState() != 1:
            startIndex = self._commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self._commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + \
                                self._commentEndExpression.matchedLength()

            self.setFormat(
                startIndex, commentLength, self._multiLineCommentFormat)
            startIndex = self._commentStartExpression.indexIn(
                text, startIndex + commentLength)
